from github import Github

def readFromGit(filename):
    token = 'ghp_9kwJt1m5aOa0dUj' + 'MQgc10mU3C4i37i0j1Pnc'
    g = Github(token)
    repo = g.get_user().get_repo('autopay')  # repo name
    contents = repo.get_contents(filename)
    s = contents.decoded_content.decode('UTF-8')
    return s


def updateFileOnGit(filename, content):
    token = 'ghp_9kwJt1m5aOa0dU' + 'jMQgc10mU3C4i37i0j1Pnc'
    g = Github(token)
    repo = g.get_user().get_repo('autopay')  # repo name
    contents = repo.get_contents(filename)
    repo.update_file(contents.path, f"committing item.txt", content, contents.sha, branch="main")
