from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager(username="memsharded", channel="testing",
                                 visual_versions=["10", "11", "12", "14"])
    builder.add_common_builds(shared_option_name="Protobuf:shared")
    builder.run()
