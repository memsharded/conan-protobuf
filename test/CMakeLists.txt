PROJECT(MyHello)
cmake_minimum_required(VERSION 2.8)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

if (MSVC)
  add_definitions(/MP)
endif (MSVC)

ADD_EXECUTABLE(client client.cpp message.pb.cc)
TARGET_LINK_LIBRARIES(client ${CONAN_LIBS})
