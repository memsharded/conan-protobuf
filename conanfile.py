from conans import ConanFile, CMake, tools, ConfigureEnvironment
import os
import shutil


class ProtobufConan(ConanFile):
    """ ONGOING WORK, tested just in Win VS 12
    """
    name = "Protobuf"
    version = "2.6.1"
    url = "https://github.com/memsharded/conan-protobuf.git"
    settings = "os", "compiler", "build_type", "arch"
    exports = "CMakeLists.txt", "*.cmake", "extract_includes.bat.in"
    options = {"static": [True, False]}
    default_options = "static=False"
    requires = "zlib/1.2.8@lasote/stable"
    generators = "cmake"

    def config(self):
        self.options["zlib"].shared = not self.options.static

    def source(self):
        tools.download("https://github.com/google/protobuf/"
                       "releases/download/v2.6.1/protobuf-2.6.1.zip",
                       "protobuf.zip")
        tools.unzip("protobuf.zip")
        os.unlink("protobuf.zip")
        os.makedirs("protobuf-2.6.1/cmake")
        shutil.move("CMakeLists.txt", "protobuf-2.6.1/cmake")
        shutil.move("libprotobuf.cmake", "protobuf-2.6.1/cmake")
        shutil.move("libprotobuf-lite.cmake", "protobuf-2.6.1/cmake")
        shutil.move("libprotoc.cmake", "protobuf-2.6.1/cmake")
        shutil.move("protoc.cmake", "protobuf-2.6.1/cmake")
        shutil.move("tests.cmake", "protobuf-2.6.1/cmake")
        shutil.move("extract_includes.bat.in", "protobuf-2.6.1/cmake")

    def build(self):
        if self.settings.os == "Windows":
            args = ['-DBUILD_TESTING=OFF']
            args += ['-DBUILD_SHARED_LIBS=%s' % ('OFF' if self.options.static else 'ON')]

            cmake = CMake(self.settings)
            self.run('cd protobuf-2.6.1/cmake && cmake . %s %s' % (cmake.command_line, ' '.join(args)))
            self.run("cd protobuf-2.6.1/cmake && cmake --build . %s" % cmake.build_config)
        else:
            env = ConfigureEnvironment(self.deps_cpp_info, self.settings)

            concurrency = 1
            try:
                import multiprocessing
                concurrency = multiprocessing.cpu_count()
            except (ImportError, NotImplementedError):
                pass

            self.run("chmod +x protobuf-2.6.1/autogen.sh")
            self.run("chmod +x protobuf-2.6.1/configure")
            self.run("cd protobuf-2.6.1 && ./autogen.sh")

            args = []
            if self.options.static:
                args += ['--disable-shared']

            self.run("cd protobuf-2.6.1 && %s ./configure %s" % (env.command_line, ' '.join(args)))
            self.run("cd protobuf-2.6.1 && make -j %s" % concurrency)

    def package(self):
        self.copy_headers("*.h", "protobuf-2.6.1/src")

        if self.settings.os == "Windows":
            self.copy("*.lib", "lib", "protobuf-2.6.1/cmake", keep_path=False)
            self.copy("protoc.exe", "bin", "protobuf-2.6.1/cmake/bin", keep_path=False)

            if not self.options.static:
                self.copy("*.dll", "bin", "protobuf-2.6.1/cmake/bin", keep_path=False)
        else:
            # Copy the libs to lib
            if self.options.static:
                self.copy("*.a", "lib", "protobuf-2.6.1/src/.libs", keep_path=False)
            else:
                self.copy("*.so*", "lib", "protobuf-2.6.1/src/.libs", keep_path=False)
            # Copy the exe to bin
            self.copy("protoc", "bin", "protobuf-2.6.1/src/", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["libprotobuf"]
        else:
            self.cpp_info.libs = ["libprotobuf.a"] if self.options.static else ["libprotobuf.so.9"]
