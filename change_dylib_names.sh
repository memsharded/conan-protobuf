for BINARY in $(find . -type f | grep '\.dylib$') protoc; do
     for LINK_DESTINATION in $(otool -L $BINARY | grep libproto | cut -f 1 -d' '); do
         install_name_tool -change "$LINK_DESTINATION" "@executable_path/$(basename $LINK_DESTINATION)" "$BINARY"
     done
done
