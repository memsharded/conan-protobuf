from conans import ConanFile, CMake
import os


class ProtobufTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "Protobuf/2.6.1@memsharded/testing"
    generators = "cmake"

    def build(self):
        self.run('%s message.proto --cpp_out="."' % os.path.join('.', 'bin', 'protoc'))
        cmake = CMake(self.settings)
        self.run('cmake . %s' % cmake.command_line)
        self.run("cmake --build . %s" % cmake.build_config)
        if self.settings.os == "Macos":
            self.run("cd bin; for LINK_DESTINATION in $(otool -L client | grep libproto | cut -f 1 -d' '); do install_name_tool -change \"$LINK_DESTINATION\" \"@executable_path/$(basename $LINK_DESTINATION)\" client; done")

    def imports(self):
        self.copy("protoc.exe", "bin", "bin") # Windows
        self.copy("protoc", "bin", "bin") # Linux / Macos
        self.copy("libproto*.9.dylib", "bin", "bin") # Macos (when options.static=False)

    def test(self):
        self.run(os.path.join(".", "bin", "client"))
