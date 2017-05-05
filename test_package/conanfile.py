from conans import ConanFile, CMake
import os


class ProtobufTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "Protobuf/3.3.0@memsharded/testing"   # FIXME
    generators = "cmake"

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "%s" %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy("protoc.exe",        "bin", "bin")  # Windows
        self.copy("protoc",            "bin", "bin")  # Linux / Macos
        self.copy("libproto*.*.dylib", "bin", "bin")  # Macos (when Protobuf:shared=True)
        self.copy("libproto*.dll",     "bin", "bin")  # Windows (when Protobuf:shared=True)
        self.copy("zlib*.dll",         "bin", "bin")  # Windows (when zlib:shared=True)

    def test(self):
        self.run(os.path.join(".", "bin", "client"))
