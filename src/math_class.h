#pragma once
#include <utility>
#include <iostream>

class IntTest {
private:
	int *p_;
	
	void reset();
public:

	IntTest();
	explicit IntTest(int v);

	IntTest(const IntTest& other);
	
	IntTest& operator = (const IntTest& other); 

	~IntTest();
	
	bool has_value() const;

	void set(int v);

	int value () const;
		
	void swap(IntTest& other);
};
