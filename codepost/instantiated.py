from .models import assignments as _assignments
from .models import courses as _courses
from .models import course_rosters as _course_rosters
from .models import submissions as _submissions
from .models import files as _files
from .models import comments as _comments
from .models import sections as _sections
from .models import rubric_categories as _rubric_categories
from .models import rubric_comments as _rubric_comments
from .models import test_categories as _test_categories
from .models import test_cases as _test_cases
from .models import submission_tests as _submission_tests
from .models import file_templates as _file_templates

assignment = _assignments.Assignments(static=True)
course = _courses.Courses(static=True)
roster = _course_rosters.CourseRosters(static=True)
submission = _submissions.Submissions(static=True)
file = _files.Files(static=True)
comment = _comments.Comments(static=True)
section = _sections.Sections(static=True)
rubric_category = _rubric_categories.RubricCategories(static=True)
rubric_comment = _rubric_comments.RubricComments(static=True)
test_category = _test_categories.TestCategories(static=True)
test_case = _test_cases.TestCases(static=True)
submission_test = _submission_tests.SubmissionTests(static=True)
file_template = _file_templates.FileTemplates(static=True)
