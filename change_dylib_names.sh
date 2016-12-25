#!/usr/bin/env bash
for BINARY in $(find . -type f | grep '\.dylib$') protoc; do
     for LINK_DESTINATION in $(otool -L ${BINARY} | grep libproto | grep -v : | cut -f 1 -d' '); do
         BINARY_BASE=$(basename ${BINARY})
         LINK_BASE=$(basename ${LINK_DESTINATION})

         if [[ ${BINARY_BASE} == ${LINK_BASE} ]]; then
            install_name_tool -id "@executable_path/${LINK_BASE}" "$BINARY"
         else
            install_name_tool -change "${LINK_DESTINATION}" "@executable_path/${LINK_BASE}" "${BINARY}"
         fi
     done
done
