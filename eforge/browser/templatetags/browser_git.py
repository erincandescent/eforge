from django import template
import git

register = template.Library()

@register.tag
def git_blame(parser, token):
    try:
        tag_name, repo, revision, file = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments" % token.contents.split()[0]
    return GitBlameNode(repo, revision, file)

class GitBlameNode(template.Node):
    def __init__(self, repo, revision, file):
        self.repo     = template.Variable(repo)
        self.revision = template.Variable(revision)
        self.file     = template.Variable(file)

    def render(self, context):
        try:
            repo = self.repo.resolve(context)
            rev  = self.revision.resolve(context)
            file = self.file.resolve(context)
            return git.Blob.blame(repo, rev, file)
        except template.VariableDoesNotExist:
            return ''
        except Exception, e:
            return str(e)


@register.tag
def git_is_file(parser, token):
    try:
        tag_name, file, as, var = toke.split_contents()
    except ValueError:
         raise template.TemplateSyntaxError, "%r tag called wrong" % token.contents.split()[0]
    return GitIsFileNode(file, var)

class GitIsFileNode(template.Node):
    def __init__(self, file, var):
        self.file     = template.Variable(file)
        self.var_name = var

    def render(self, context):
        file = self.file.resolve(context)
        context[self.var_name] = isinstance(file, git.blob.Blob)

