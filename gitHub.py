from github import Github

def readFromGit(filename):
    token = 'ghp_OtNctAl06i8oKEOZS' + 'uWBuLRpymWVPu4bgNUP'
    g = Github(token)
    repo = g.get_user().get_repo('autopay')  # repo name
    contents = repo.get_contents(filename)
    s = contents.decoded_content.decode('UTF-8')
    return s


def updateFileOnGit(filename, content):
    token = 'ghp_OtNctAl06i8oKEOZS' + 'uWBuLRpymWVPu4bgNUP'
    g = Github(token)
    repo = g.get_user().get_repo('autopay')  # repo name
    contents = repo.get_contents(filename)
    repo.update_file(contents.path, f"committing item.txt", content, contents.sha, branch="main")
