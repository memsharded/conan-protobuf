from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from conans.tools import os_info, SystemPackageTool
import shutil
import os


class ProtobufConan(ConanFile):
    """
    Requires autogen/make/conf, libtool on Linux

    If shared=True on Macos you will need to copy *.dylib to the executable (bin) directory
    See import() in test_package/conanfile.py for an example
    """
    name = "Protobuf"
    version = "3.3.0"
    _sha256 = '9a36bc1265fa83b8e818714c0d4f08b8cec97a1910de0754a321b11e66eb76de'
    _shared_lib_version = 10

    _source_dir = "protobuf-%s" % version
    url = "https://github.com/memsharded/conan-protobuf.git"
    license = "https://github.com/google/protobuf/blob/master/LICENSE"
    requires = "zlib/1.2.11@lasote/stable"
    settings = "os", "compiler", "build_type", "arch"
    exports = "change_dylib_names.sh"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=False"
    generators = "cmake"

    def config_options(self):
        self.options["zlib"].shared = self.options.shared
        # if self.settings.compiler == 'gcc' and float(self.settings.compiler.version.value) >= 5.1:
        #     if self.settings.compiler.libcxx != 'libstdc++11':
        #         raise ConanException("You must use the setting compiler.libcxx=libstdc++11")

    def source(self):
        download_filename = "v%s.tar.gz" % self.version
        tools.download('https://github.com/google/protobuf/archive/%s' % download_filename, download_filename)
        tools.check_sha256(download_filename, self._sha256)
        tools.unzip(download_filename)
        os.unlink(download_filename)
        shutil.copy("change_dylib_names.sh", "%s/cmake" % self._source_dir)

    def system_requirements(self):
        if os_info.is_linux:
            installer = SystemPackageTool()
            for pkg in ["autoconf", "automake", "libtool", "curl", "make", "g++", "unzip"]:
                installer.install(pkg)

    def build(self):
        if self.settings.os == "Windows":
            defs = dict()
            defs['protobuf_BUILD_TESTS'] = 'OFF'
            defs['ZLIB_ROOT']=self.deps_cpp_info['zlib'].rootpath
            defs['BUILD_SHARED_LIBS'] = 'ON' if self.options.shared else 'OFF'
            if self.settings.compiler == "Visual Studio":
                defs['protobuf_MSVC_STATIC_RUNTIME'] = 'ON' if "MT" in str(self.settings.compiler.runtime) else 'OFF'
            defs['CMAKE_INSTALL_PATH'] = self.package_folder
            cmake = CMake(self)
            cmake_dir = os.path.sep.join([self._source_dir, "cmake"])
            cmake.configure(source_dir='.', build_dir=cmake_dir, defs=defs)
            cmake.build()
            cmake.install()            
        else:
            env = AutoToolsBuildEnvironment(self)
            with tools.environment_append(env.vars):
                cpus = tools.cpu_count()

                self.run("./autogen.sh", cwd=self._source_dir)

                args = ['--disable-dependency-tracking', '--with-zlib']
                if not self.options.shared:
                    args += ['--disable-shared']
                if self.options.shared or self.options.fPIC:
                    args += ['"CFLAGS=-fPIC" "CXXFLAGS=-fPIC"']

                self.run("./configure %s" % (' '.join(args)), cwd=self._source_dir)
                self.run("make -j %s" % cpus, cwd=self._source_dir)

    def package(self):
        self.copy("*.h", "include", "%s/src" % self._source_dir)
        self.copy("descriptor.proto", "include/google/protobuf", "protobuf-%s/src/google/protobuf" % self.version, keep_path=False)
        self.copy("plugin.proto", "include/google/protobuf/compiler", "protobuf-%s/src/google/protobuf/compiler" % self.version, keep_path=False)

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                pass
            elif self.settings.compiler == "gcc":
                self.copy("*.a", "lib", "%s/cmake" % self._source_dir, keep_path=False)
            self.copy("*.exe", "bin", "%s/cmake" % self._source_dir, keep_path=False)

            if self.options.shared:
                self.copy("*.dll", "bin", "%s/cmake" % self._source_dir, keep_path=False)
        else:
            if self.settings.os == "Macos":
                if not self.options.shared:
                    self.copy("protoc", "bin", "%s/src/" % self._source_dir, keep_path=False)
                    self.copy("*.a", "lib", "%s/src/.libs" % self._source_dir, keep_path=False)
                else:
                    # Change *.dylib dependencies and ids to be relative to @executable_path
                    self.run("bash ../../cmake/change_dylib_names.sh", cwd="%s/src/.libs" % self._source_dir)
                    self.copy("*.dylib", "bin", "%s/src/.libs" % self._source_dir,
                              keep_path=False, symlinks=True)
                    self.copy("*.dylib", "lib", "%s/src/.libs" % self._source_dir,
                              keep_path=False, symlinks=True)

                    # "src/protoc" may be a wrapper shell script which execute "src/.libs/protoc".
                    # Copy "src/.libs/protoc" instead of "src/protoc"
                    self.copy("protoc", "bin", "%s/src/.libs/" % self._source_dir, keep_path=False)
            else:
                self.copy("protoc", "bin", "%s/src/" % self._source_dir, keep_path=False)
                if not self.options.shared:
                    self.copy("*.a", "lib", "%s/src/.libs" % self._source_dir, keep_path=False)
                else:
                    self.copy("*.so*", "lib", "%s/src/.libs" % self._source_dir, keep_path=False, symlinks=True)

    def package_info(self):
        if self.settings.os == "Windows":
            lib_prefix = "lib" if self.settings.compiler == "Visual Studio" else ""
            lib_suffix = "d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.libs = ["%sprotobuf%s" % (lib_prefix, lib_suffix)]
            if self.options.shared:
                self.cpp_info.defines = ["PROTOBUF_USE_DLLS"]
        elif self.settings.os == "Macos":
            self.cpp_info.libs = ["libprotobuf.a"] if not self.options.shared \
                else ["libprotobuf.%d.dylib" % self._shared_lib_version]
        else:
            self.cpp_info.libs = ["protobuf"]
