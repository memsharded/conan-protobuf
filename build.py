from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager(username="memsharded", channel="testing",
                                 visual_versions=["10", "12", "14"])
    builder.add_common_builds(shared_option_name="Protobuf:shared")
    filtered_builds = []
    for settings, options in builder.builds:
        if settings["arch"] == "x86_64":
             filtered_builds.append([settings, options])
    builder.builds = filtered_builds
    builder.run()
