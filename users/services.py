from users.models import User
from settings.models import Branch, BranchAssignment


def create_new_user(request):
    data = {
        "username": request["username"],
        "email_address": request["email_address"],
    }
    user = User.objects.create(**data)
    user.set_password(request["password"])
    user.save()
    return user


def update_branch_assignments(request):
    request_branches = request.data["branch"]
    assignment = BranchAssignment.objects.get(user__user_id=request.data["user_id"])
    added_branches = []

    for branch in request_branches:
        branch_obj = Branch.objects.get(branch_id=branch["branch_id"])
        assignment.branch.add(branch_obj)
        added_branches.append(branch_obj.id)

    for branch in assignment.branch.all():
        if branch.id not in added_branches:
            assignment.branch.remove(branch)


def create_user_logs(request):
    pass