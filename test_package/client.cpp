#include <iostream>
#include <string>
#include <stdexcept>

#include <google/protobuf/compiler/code_generator.h>  // for ParseGeneratorParameter

#include "message.pb.h"

using namespace std;

int main() {
  GOOGLE_PROTOBUF_VERIFY_VERSION;

  tutorial::AddressBook address_book;
  tutorial::Person* person = address_book.add_person();

  person->set_id(123);
  person->set_name("John");
  person->set_email("john@gmail.com");
  tutorial::Person::PhoneNumber* phone_number = person->add_phone();
  phone_number->set_number("1234567");
  phone_number->set_type(tutorial::Person::MOBILE);

  string output;
  address_book.SerializeToString(&output);

  tutorial::AddressBook address_book2;
  address_book2.ParseFromString(output);

  string debug_output = address_book.DebugString();
  string debug_output2 = address_book2.DebugString();

  cout << address_book2.DebugString() << std::endl;

  if (debug_output != debug_output2) {
      throw std::runtime_error("address_book != address_book2");
  }

  google::protobuf::compiler::ParseGeneratorParameter("", nullptr);
  return 0;
}