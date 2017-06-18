from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(username="memsharded", channel="testing", archs = ["x86_64"])
    builder.add_common_builds(shared_option_name="Protobuf:shared")
    builder.run()
