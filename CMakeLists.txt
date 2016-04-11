cmake_minimum_required(VERSION 2.8)

project(protobuf C CXX)
include(../../conanbuildinfo.cmake)
conan_basic_setup()

option(BUILD_TESTING "Build tests" ON)
option(BUILD_SHARED_LIBS "Build Shared Libraries" OFF)

add_definitions(-DGOOGLE_PROTOBUF_CMAKE_BUILD)
add_definitions(-DHAVE_ZLIB)

include(../../conanbuildinfo.cmake)
conan_basic_setup()

find_package(Threads REQUIRED)
if (CMAKE_USE_PTHREADS_INIT)
  add_definitions(-DHAVE_PTHREAD)
endif (CMAKE_USE_PTHREADS_INIT)

set(HAVE_ZLIB 1)

if (MSVC)
  if (BUILD_SHARED_LIBS)
    add_definitions(-DPROTOBUF_USE_DLLS)
  endif (BUILD_SHARED_LIBS)
  add_definitions(/wd4244 /wd4267 /wd4018 /wd4355 /wd4800 /wd4251 /wd4996 /wd4146 /wd4305)
  add_definitions(/MP)
endif (MSVC)

if (MSVC)
  string(REPLACE "/" "\\" PROTOBUF_SOURCE_WIN32_PATH ${protobuf_SOURCE_DIR})
  string(REPLACE "/" "\\" PROTOBUF_BINARY_WIN32_PATH ${protobuf_BINARY_DIR})
  configure_file(extract_includes.bat.in extract_includes.bat)
endif (MSVC)

if (MSVC)
  if (CONAN_COMPILER_VERSION STREQUAL "14")
    # error C2338: <hash_map> is deprecated and will be REMOVED. Please use <unordere
    # d_map>. You can define _SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS to acknowledge
    # that you have received this warning.
    add_definitions(-D_SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS)
  endif ()
endif (MSVC)

get_filename_component(protobuf_source_dir ${protobuf_SOURCE_DIR} PATH)

include_directories(
  ${CONAN_INCLUDE_DIRS}
  ${protobuf_BINARY_DIR}
  ${protobuf_source_dir}/src
  ../vsprojects)

if (MSVC)
  # Add the "lib" prefix for generated .lib outputs.
  set(LIB_PREFIX lib)
else (MSVC)
  # When building with "make", "lib" prefix will be added automatically by
  # the build tool.
  set(LIB_PREFIX)
endif (MSVC)

include(libprotobuf-lite.cmake)
include(libprotobuf.cmake)
include(libprotoc.cmake)
include(protoc.cmake)
if (BUILD_TESTING)
  include(tests.cmake)
endif (BUILD_TESTING)