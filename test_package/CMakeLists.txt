project(MyHello)
cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if (MSVC)
  add_definitions(/MP)
endif (MSVC)

include_directories(${CMAKE_BINARY_DIR})
add_executable(client client.cpp message.pb.cc)
target_link_libraries(client ${CONAN_LIBS})
