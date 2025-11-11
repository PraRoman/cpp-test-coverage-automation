#include <iostream>
#include <gtest/gtest.h>
#include "../src/math.h"

TEST(Math, Add_Positive) {
	EXPECT_EQ(addition(2,3), 5);
}

TEST(Math, Add_Negative){
	EXPECT_EQ(addition(-4, -1), -5);
}

int main(int argc, char** argv) {
	::testing::InitGoogleTest(&argc, argv);
	return RUN_ALL_TESTS();
}

/*
int main() {
    int fails = 0;
    
	if (addition(2,3) != 5) {
		std::cerr << "add failed" << std::endl; 
		++fails;
	}
	if (fails) {
		std::cerr << "FAIL, " << fails << "fails" << std::endl;
	}
	std::cout << "Ok" << std::endl;

	return 0;
}*/
