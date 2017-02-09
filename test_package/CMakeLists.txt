project(MyHello)
cmake_minimum_required(VERSION 2.8)

set(PROTOS message.proto)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(Protobuf_LIBRARY ${CONAN_PROTOBUF_ROOT} CACHE PATH "Protobuf library dir")
find_package(Protobuf)

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTOS})
include_directories(${CMAKE_CURRENT_BINARY_DIR})

if (MSVC)
  add_definitions(/MP)
endif (MSVC)

include_directories(${CMAKE_BINARY_DIR})
add_executable(client client.cpp message.pb.cc)
target_link_libraries(client PRIVATE ${CONAN_LIBS_PROTOBUF})

