cmake_minimum_required(VERSION 3.16)
project (test_of_script LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(math STATIC src/math.cpp)
target_include_directories(math PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

find_package(GTest REQUIRED)
find_package(Threads REQUIRED)

enable_testing()

#Test 1

add_executable(math_tests_func tests/test_func.cpp)

target_include_directories(math_tests_func PRIVATE ${GTEST_INCLUDE_DIRS})
target_link_libraries(math_tests_func
    PRIVATE
	math
	${GTEST_LIBRARIES}
	Threads::Threads)

#Test 2

add_executable(math_tests_class 
    tests/test_class.cpp
    src/math_class.cpp
)

target_include_directories(math_tests_class PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src ${GTEST_INCLUDE_DIRS})
target_link_libraries(math_tests_class
    PRIVATE 
	math 
	${GTEST_LIBRARIES}
	Threads::Threads)

include(GoogleTest)
gtest_discover_tests(math_tests_func)
gtest_discover_tests(math_tests_class)
