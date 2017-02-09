from conans import ConanFile, CMake, tools, ConfigureEnvironment
import shutil
import os

from conans.errors import ConanException


class ProtobufConan(ConanFile):
    """
    Requires autogen/make/conf, libtool on Linux

    If shared=True on Macos you will need to copy *.dylib to the executable (bin) directory
    See import() in test_package/conanfile.py for an example
    """
    name = "Protobuf"
    version = "3.0.2"
    _sha256 = 'b700647e11556b643ccddffd1f41d8cb7704ed02090af54cc517d44d912d11c1'
    _shared_lib_version = 10

    _source_dir = "protobuf-%s" % version
    url = "https://github.com/memsharded/conan-protobuf.git"
    license = "https://github.com/google/protobuf/blob/master/LICENSE"
    requires = "zlib/1.2.8@lasote/stable"
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

    def build(self):
        if self.settings.os == "Windows":
            args = ['-Dprotobuf_BUILD_TESTS=OFF']
            args += ['-DZLIB_ROOT=%s' % dict(self.deps_cpp_info.dependencies)["zlib"].rootpath]
            args += ['-DBUILD_SHARED_LIBS=%s' % ('ON' if self.options.shared else 'OFF')]
            cmake = CMake(self.settings)
            cmake_dir = os.path.sep.join([self._source_dir, "cmake"])
            self.run('cmake . %s %s' % (cmake.command_line, ' '.join(args)), cwd=cmake_dir)
            self.run("cmake --build . %s" % cmake.build_config, cwd=cmake_dir)
        else:
            env = ConfigureEnvironment(self)
            cpus = tools.cpu_count()

            self.run("./autogen.sh", cwd=self._source_dir)

            args = ['--disable-dependency-tracking', '--with-zlib']
            if not self.options.shared:
                args += ['--disable-shared']
            if self.options.shared or self.options.fPIC:
                args += ['"CFLAGS=-fPIC" "CXXFLAGS=-fPIC"']

            self.run("%s ./configure %s" % (env.command_line, ' '.join(args)), cwd=self._source_dir)
            self.run("make -j %s" % cpus, cwd=self._source_dir)

    def package(self):
        self.copy_headers("*.h", "%s/src" % self._source_dir)

        if self.settings.os == "Windows":
            self.copy("*.lib", "lib", "%s/cmake" % self._source_dir, keep_path=False)
            self.copy("protoc.exe", "bin", "%s/cmake/bin" % self._source_dir, keep_path=False)

            if self.options.shared:
                self.copy("*.dll", "bin", "%s/cmake/bin" % self._source_dir, keep_path=False)
        else:
            if self.settings.os == "Macos":
                if not self.options.shared:
                    self.copy("protoc", "bin", "%s/src/" % self._source_dir, keep_path=False)
                    self.copy("*.a", "lib", "%s/src/.libs" % self._source_dir, keep_path=False)
                else:
                    # Change libproto*.dylib dependencies and ids to be relative to @executable_path
                    self.run("cd %s/src/.libs && bash ../../cmake/change_dylib_names.sh" % self._source_dir)
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
            self.cpp_info.libs = ["libprotobuf"]
            if self.options.shared:
                self.cpp_info.defines = ["PROTOBUF_USE_DLLS"]
        elif self.settings.os == "Macos":
            self.cpp_info.libs = ["libprotobuf.a"] if not self.options.shared \
                else ["libprotobuf.%d.dylib" % self._shared_lib_version]
        else:
            self.cpp_info.libs = ["protobuf"]
