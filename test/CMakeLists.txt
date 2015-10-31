PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(client client.cpp message.pb.cc)
TARGET_LINK_LIBRARIES(client ${CONAN_LIBS})
