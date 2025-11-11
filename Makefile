CXX = g++
CXXFLAGS = -std=c++11 -O0 -g --coverage
LDFLAGS = --coverage
TARGET = test_add
SRC = main.cpp test_add.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS)

test: $(TARGET)
	./$(TARGET)

clean:
	rm -rf $(TARGET) *.o *.gcno *.gcda *.gcov coverage.info
	rm -rf coverage_html
