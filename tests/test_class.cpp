#include <gtest/gtest.h>
#include "../src/math_class.h"

TEST(ClassTest, IsEmpty) {
	IntTest a;
	EXPECT_FALSE(a.has_value());
}

TEST(ClassTest, SetValue) {
	IntTest a(10);
	EXPECT_TRUE(a.has_value());
	EXPECT_EQ(a.value(), 10);
}

TEST(ClassTest, SetOnEmptyVar) {
	IntTest a;
	a.set(20);
	EXPECT_TRUE(a.has_value());
	EXPECT_EQ(a.value(), 20);
}

TEST(ClassTest, CopyOfVar) {
	IntTest a(30);
	IntTest b = a;
	EXPECT_TRUE(a.has_value());
	EXPECT_TRUE(b.has_value());
	EXPECT_EQ(a.value(), 30);
	EXPECT_EQ(b.value(), 30);
	
	b.set(100);
	EXPECT_EQ(a.value(), 30);
	EXPECT_EQ(b.value(), 100);
}

TEST(ClassTest, SelfCopy) {
	IntTest a(40), b(50);
	b = a;
	EXPECT_EQ(a.value(), 40);
	EXPECT_EQ(b.value(), 40);

	b = b;
	EXPECT_EQ(b.value(), 40);
}

TEST(ClassTest, Swap) {
	IntTest a(60), b(70);
	a.swap(b);
	EXPECT_EQ(a.value(), 70);
	EXPECT_EQ(b.value(), 60);
}

int main(int argc, char **argv) {
	::testing::InitGoogleTest(&argc, argv);

	return RUN_ALL_TESTS();
}
