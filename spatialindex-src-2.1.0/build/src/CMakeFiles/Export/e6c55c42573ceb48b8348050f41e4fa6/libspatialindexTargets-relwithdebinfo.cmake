#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "spatialindex" for configuration "RelWithDebInfo"
set_property(TARGET spatialindex APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(spatialindex PROPERTIES
  IMPORTED_IMPLIB_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/spatialindex-64.lib"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/spatialindex-64.dll"
  )

list(APPEND _cmake_import_check_targets spatialindex )
list(APPEND _cmake_import_check_files_for_spatialindex "${_IMPORT_PREFIX}/lib/spatialindex-64.lib" "${_IMPORT_PREFIX}/bin/spatialindex-64.dll" )

# Import target "spatialindex_c" for configuration "RelWithDebInfo"
set_property(TARGET spatialindex_c APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(spatialindex_c PROPERTIES
  IMPORTED_IMPLIB_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/spatialindex_c-64.lib"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/spatialindex_c-64.dll"
  )

list(APPEND _cmake_import_check_targets spatialindex_c )
list(APPEND _cmake_import_check_files_for_spatialindex_c "${_IMPORT_PREFIX}/lib/spatialindex_c-64.lib" "${_IMPORT_PREFIX}/bin/spatialindex_c-64.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
