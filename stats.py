from tabulate import tabulate


def dedup(l):
    return list(set(l))


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
:: STATS ::
Repo count                    : {self.RepoCount}
Repos containing secrets      : {len(self.Repos)}
Detections                    : {len(self.Findings)}
Unique Secrets                : {len(self.DeduplicatedBySecret)}
auto-Verified Active Secrets  : {len(self.VerifiedSecrets)}

========================= DETECTIONS BY TOOL ===============================
{tabulate(by_source, ["Source","Occurance"])}

====================== UNIQUE SECRETS BY TYPE ==============================
{tabulate(by_type, ["Type","Occurance"])}

====================== DETECTIONS BY EXTENSION =============================
{tabulate(by_extension, ["Extension","Occurance"])}

====================== DETECTIONS BY REPOSITORY ============================
{tabulate(by_repository, ["Repository","Occurance"])}
        """
