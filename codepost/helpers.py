from .models import assignments as _assignments
from .models import courses as _courses
from .models import course_rosters as _course_rosters
from .models import submissions as _submissions
from .models import files as _files
from .models import comments as _comments
from .models import sections as _sections
from .models import rubric_categories as _rubric_categories
from .models import rubric_comments as _rubric_comments

assignment = _assignments.Assignments(static=True)
course = _courses.Courses(static=True)
roster = _course_rosters.CourseRosters(static=True)
submission = _submissions.Submissions(static=True)
file = _files.Files(static=True)
comment = _comments.Comments(static=True)
section = _sections.Sections(static=True)
rubric_category = _rubric_categories.RubricCategories(static=True)
rubric_comment = _rubric_comments.RubricComments(static=True)
