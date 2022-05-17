from os import linesep


def dedup(l):
    return list(set(l))


def template_table(list, headings, title):
    ret = header_row(title)
    if headings != []:
        ret += template_row(*headings)
        ret += header_row()
    for item in list:
        ret += template_row(*item)
    ret += header_row()
    return ret


def template_row(a, b):
    return ("| %.56s" % a).ljust(61) + " | " + ("%.8s" % b).ljust(10) + " |" + linesep


def header_row(header=""):
    if len(header) > 0:
        header = f" {header.upper()} "
    if len(header) % 2:
        header += "="
    l = len(template_row(" ", " ")) - 2 - len(linesep)
    inject_index = int((l / 2) - (len(header) / 2))
    return f"|{'=' * inject_index}{header}{'=' * inject_index}|{linesep}"


class Stats:
    def __init__(self, findings, repo_count):
        self.Findings = findings
        self.RepoCount = repo_count

    @property
    def Repos(self):
        return dedup([f.repository for f in self.Findings])

    @property
    def DeduplicatedBySecret(self):
        d = {}
        for f in self.Findings:
            d[f.hashed_secret] = f
        return d.values()

    @property
    def Secrets(self):
        return [f.hashed_secret for f in self.DeduplicatedBySecret]

    @property
    def VerifiedSecrets(self):
        return [
            f.hashed_secret for f in self.DeduplicatedBySecret if f.verified == True
        ]

    def FilteredByKV(self, key, value, deduped=True):
        findings = self.DeduplicatedBySecret if deduped else self.Findings
        return [f.hashed_secret for f in findings if f.__dict__[key] == value]

    @property
    def Observeddetector_types(self):
        return dedup([f.detector_type for f in self.DeduplicatedBySecret])

    @property
    def ObservedExtensions(self):
        return dedup([f.extension for f in self.Findings])

    @property
    def ObservedRepositories(self):
        return dedup([f.repository for f in self.Findings])

    @property
    def ObservedSources(self):
        return dedup([f.source for f in self.Findings])

    def ByExtension(self, e):
        return self.FilteredByKV("extension", e, False)

    def Bydetector_type(self, t):
        return self.FilteredByKV("detector_type", t)

    def ByRepository(self, r):
        return self.FilteredByKV("repository", r, False)

    def BySource(self, s):
        return self.FilteredByKV("source", s, False)

    def Report(self):
        general_stats = [
            ["Repo count", self.RepoCount],
            ["Repos containing secrets", len(self.Repos)],
            ["Detections", len(self.Findings)],
            ["Unique Secrets", len(self.DeduplicatedBySecret)],
        ]
        by_type = [
            (t, len(self.Bydetector_type(t))) for t in self.Observeddetector_types
        ]
        by_type.sort(key=lambda x: x[1], reverse=True)
        by_extension = [(e, len(self.ByExtension(e))) for e in self.ObservedExtensions]
        by_extension.sort(key=lambda x: x[1], reverse=True)
        by_repository = [
            (r, len(self.ByRepository(r))) for r in self.ObservedRepositories
        ]
        by_repository.sort(key=lambda x: x[1], reverse=True)
        by_source = [(s, len(self.BySource(s))) for s in self.ObservedSources]
        by_source.sort(key=lambda x: x[1], reverse=True)
        return f"""
{template_table(general_stats, [], "STATS")}

{template_table(by_source, ["Source","Count"], "Detections by tool")}

{template_table(by_type, ["Type","Count"], "Unique Secrets by type")}

{template_table(by_extension, ["Extension","Count"], "Detections by extension")}

{template_table(by_repository, ["Repository","Count"], "Detections by repository")}
        """
