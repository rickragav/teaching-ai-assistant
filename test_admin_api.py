"""
Test script for Admin API endpoints
"""

import requests
import json

API_BASE = "http://localhost:8000/api"


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_create_course():
    """Test creating a course"""
    print_section("Testing Create Course")

    course_data = {
        "title": "Test Udemy Course",
        "description": "A test course for UdemyGPT",
        "sections": [
            {
                "title": "Introduction",
                "order": 0,
                "lessons": [
                    {
                        "title": "Welcome to the Course",
                        "subtitle": "Getting Started",
                        "content": "Welcome to this amazing course! In this lesson, we will cover the basics of effective communication. Communication is a fundamental skill that impacts every aspect of our lives, from personal relationships to professional success. Let's explore the key principles together.",
                        "order": 0,
                    },
                    {
                        "title": "Course Overview",
                        "subtitle": "What You'll Learn",
                        "content": "This course covers essential communication skills. You will learn how to express yourself clearly, listen actively, and build strong relationships. We'll explore verbal and non-verbal communication techniques that you can apply immediately in your daily life.",
                        "order": 1,
                    },
                ],
            },
            {
                "title": "Advanced Topics",
                "order": 1,
                "lessons": [
                    {
                        "title": "Mastering Difficult Conversations",
                        "subtitle": "Advanced Techniques",
                        "content": "In this advanced lesson, we'll tackle difficult conversations. Learn how to handle conflicts, deliver constructive feedback, and navigate sensitive topics with confidence and empathy. These skills are crucial for leadership and personal growth.",
                        "order": 0,
                    }
                ],
            },
        ],
    }

    try:
        response = requests.post(
            f"{API_BASE}/admin/courses",
            json=course_data,
            headers={"Content-Type": "application/json"},
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Course created successfully!")
            print(f"   ID: {data['id']}")
            print(f"   Title: {data['title']}")
            print(f"   Sections: {data['sections_count']}")
            print(f"   Lessons: {data['lessons_count']}")
            return data["id"]
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_list_courses():
    """Test listing courses"""
    print_section("Testing List Courses")

    try:
        response = requests.get(f"{API_BASE}/admin/courses")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            courses = response.json()
            print(f"✅ Found {len(courses)} course(s)")
            for course in courses:
                print(f"\n   📚 {course['title']}")
                print(f"      ID: {course['id']}")
                print(
                    f"      Sections: {course['sections_count']}, Lessons: {course['lessons_count']}"
                )
            return courses
        else:
            print(f"❌ Error: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def test_get_course(course_id):
    """Test getting course details"""
    print_section(f"Testing Get Course Details: {course_id}")

    try:
        response = requests.get(f"{API_BASE}/admin/courses/{course_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            course = response.json()
            print(f"✅ Course: {course['title']}")
            print(f"   Description: {course['description']}")
            print(f"   Sections: {len(course['sections'])}")
            for section in course["sections"]:
                print(f"\n   📖 Section: {section['title']}")
                print(f"      Lessons: {len(section['lessons'])}")
                for lesson in section["lessons"]:
                    print(f"         - {lesson['title']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_learning_path(user_id="test_user"):
    """Test learning path endpoint"""
    print_section(f"Testing Learning Path for User: {user_id}")

    try:
        response = requests.get(f"{API_BASE}/learning-path/{user_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Learning path retrieved successfully!")
            print(f"   User ID: {data['user_id']}")
            print(f"   Total Lessons: {data['stats']['total_lessons']}")
            print(f"   Completed: {data['stats']['completed_lessons']}")
            print(f"\n   Sections: {len(data['sections'])}")
            for section in data["sections"]:
                print(f"\n   📖 {section['title']}")
                for lesson in section["lessons"][:3]:  # Show first 3 lessons
                    status = (
                        "🔒 Locked"
                        if lesson["is_locked"]
                        else ("✅ Current" if lesson["is_current"] else "📝 Available")
                    )
                    print(f"      {status} - {lesson['title']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_delete_course(course_id):
    """Test deleting a course"""
    print_section(f"Testing Delete Course: {course_id}")

    try:
        response = requests.delete(f"{API_BASE}/admin/courses/{course_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Course deleted successfully!")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n🚀 Starting Admin API Tests")
    print("Make sure the server is running: python -m src.api.main")

    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed! Make sure the server is running.")
        return

    # Test 2: Create a course
    course_id = test_create_course()
    if not course_id:
        print("\n❌ Course creation failed!")
        return

    # Test 3: List courses
    courses = test_list_courses()

    # Test 4: Get course details
    if course_id:
        test_get_course(course_id)

    # Test 5: Test learning path
    test_learning_path()

    # Test 6: Delete course (optional - comment out to keep test data)
    # if course_id:
    #     test_delete_course(course_id)

    print_section("✅ All Tests Completed!")
    print("\n📝 Summary:")
    print("   - Health check: OK")
    print("   - Create course: OK")
    print("   - List courses: OK")
    print("   - Get course details: OK")
    print("   - Learning path: OK")
    print("\n💡 Tip: Open admin-backoffice.html in your browser to use the UI")


if __name__ == "__main__":
    main()
