from behave import fixture


def safe_add_rules(context, rules):
    # For when you look at this in the future, this isn't running at all. Figure out why.
    try:
        context.rules
    except AttributeError:
        context.rules = []

    context.rules.extend(rules)


@fixture
def wantsSSHKey(context):
    ssh_key = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAIEAuaJtfDkJfu0BhyQACpCeu6y1hWPHEN6kXbKJ4Da5ammYQrrmUjLS
WJXhU8i8tM1438ZuJiA+49ZDP/Kh6P8Hs9GulRuYDNa9a+WuZurcsKUvr5WDK67KX7mU8K
R0+1XkN6tzXTaBdjZldOGQ+V3DXAsWoWHbkzL6Cm1Iy6w57msAAAIAH+jd2h/o3doAAAAH
c3NoLXJzYQAAAIEAuaJtfDkJfu0BhyQACpCeu6y1hWPHEN6kXbKJ4Da5ammYQrrmUjLSWJ
XhU8i8tM1438ZuJiA+49ZDP/Kh6P8Hs9GulRuYDNa9a+WuZurcsKUvr5WDK67KX7mU8KR0
+1XkN6tzXTaBdjZldOGQ+V3DXAsWoWHbkzL6Cm1Iy6w57msAAAADAQABAAAAgFRV1MPQ7d
16M22AD3y9Q0AkMLuPHwss+yOOT1FLy2Tq4D/AxY6mhCW2wg3cbs79YmLXtYcgszGzUA4n
XyOJaaekEVVgmeH8214bckwSIDadtDiIBLKZJ6thQOjk7ijS2ZCq/8PQdK4j7J2/Nl9X3e
0ciE8lbU49occQl1ppE8aRAAAAQQDXkWIMdUhnSZ3LRkSBpLOEXiJ9UEHHNYg3dNZSmqK1
LhNRpiY5GJAMBGPXujt6oGyoSCLCSqU9ckOUN8I+LRtuAAAAQQDaKzn9XIkNQjtbMDO4lx
i/94me4HgbgrJjWdsmKpNJd6pMTXaIjCv992MWKIp4tv/uuMQNRuqiNHGeDZbwFDKPAAAA
QQDZ0vZDS/MF4T2nmkkZyDEzSG5bf3pzZVpopTwidC2bbKRxsvRiDMHz0+iGbtNNJKq183
UJor65LswerJbV7ERlAAAABm5vbmFtZQECAwQ=
-----END OPENSSH PRIVATE KEY-----"""

    key_file = [s + "\n" for s in ssh_key.split("\n")]
    key_file.insert(0, "file ssh_key")

    safe_add_rules(context, [["repo ssh"], key_file, ["commit"]])


@fixture
def wantsAWSSecret(context):
    safe_add_rules(
        context,
        [
            ["repo aws"],
            [
                "file aws_key",
                "aws_access_key_id = AKIAYVP4CIPPERUVIFXG\n",
                "aws_secret_access_key = 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",
            ],
            ["commit"],
        ],
    )


def branchTest(context):
    safe_add_rules(
        context,
        [
            ["repo 1"],
            [
                "file file1",
                "aws_access_key_id = AKIAYVP4CIPPERUVIFXG\n",
                "aws_secret_access_key = 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",
            ],
            [
                "file file2",
                "aws_access_key_id = AKIAYVP4CIPPERUVIFXH\n",
                "aws_secret_access_key = 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",
            ],
            ["commit"],
            ["branch dev"],
            [
                "file file3",
                "aws_access_key_id = AKIAYVP4CIPPERUVIFXI\n",
                "aws_secret_access_key = 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",
            ],
            [
                "file file4",
                "aws_access_key_id = AKIAYVP4CIPPERUVIFXJ\n",
                "aws_secret_access_key = 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",
            ],
            ["commit"],
        ],
    )


fixture_map = {
    "wantsSSHKey": wantsSSHKey,
    "wantsAWSSecret": wantsAWSSecret,
    "branchTest": branchTest,
}
