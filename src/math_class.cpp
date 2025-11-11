#include "math_class.h"

void IntTest::reset() {
	delete p_;
	p_ = nullptr;
}

//Конструктор по умолчанию
IntTest::IntTest() : p_(nullptr) {}

//Конструктор с параметром
IntTest::IntTest(int v) : p_(new int(v)) {}

//Копирующий коструктор
IntTest::IntTest(const IntTest& other)
	: p_(other.p_ ? new int(*other.p_) : nullptr) {}
	
//Копирующее присваивание
IntTest& IntTest::operator = (const IntTest& other) {
	if (this != &other) {
		IntTest tmp(other);
		swap(tmp);
	}
	return *this;
}

IntTest::~IntTest() {reset();}

//API
	
bool IntTest::has_value() const {return p_ != nullptr; }

void IntTest::set(int v) {
	if (!p_) p_ = new int(v);
	else *p_ = v;
}

int IntTest::value () const {
	if (!p_) std::cerr << "No value" << std::endl;
	return *p_;   	
}
		
void IntTest::swap(IntTest& other) {std::swap(p_, other.p_);}

