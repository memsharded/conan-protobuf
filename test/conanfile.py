from conans import ConanFile, CMake
import os


class ProtobufTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "Protobuf/2.6.1@memsharded/testing"
    generators = "cmake"

    def build(self):
        self.run('protoc message.proto --cpp_out="."')
        cmake = CMake(self.settings)
        self.run('cmake . %s' % cmake.command_line)
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy("protoc.exe", "", "bin")

    def test(self):
        self.run(os.sep.join([".", "bin", "client"]))
