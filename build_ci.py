from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager(username="memsharded", channel="testing")
    builder.add_common_builds(shared_option_name="Protobuf:shared")
    filtered_builds = []
    for settings, options in builder.builds:
        if settings["compiler.version"] in (12, 14):
             filtered_builds.append([settings, options])
    builder.builds = filtered_builds
    builder.run()
