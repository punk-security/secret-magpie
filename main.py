#TODO: remove unused dependencies
from concurrent.futures import process
from mailbox import _PartialFile
from github import Github #pygithub
from git import Repo #gitpython
from hashlib import sha256
from shutil import rmtree
from subprocess import run
from time import sleep
from multiprocessing.pool import ThreadPool
from functools import partial
from os import remove
from json import loads
from enum import Enum
from base64 import b64decode

api_token = ""
organisation = ""
parallelism = 3

def clone_repo(clone_url, pat):
    path = sha256(clone_url.encode('utf-8')).hexdigest()[0:8]
    if clone_url.lower()[0:8] != "https://":
        raise Exception(f"clone url not in expected format: '{clone_url}'")
    target = f"https://{pat}@{clone_url[8:]}"
    Repo.clone_from(target, path).remotes[0].fetch()
    return path

def onerror(func, path, exc_info):
    import stat,os
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

#TODO: Move to sep file
class DetectorTypeEnum(Enum):
  Alibaba = 0
  AMQP = 1
  AWS = 2
  Azure = 3
  Circle = 4
  Coinbase = 5
  GCP = 6
  Generic = 7
  Github = 8
  Gitlab = 9
  JDBC = 10
  RazorPay = 11
  SendGrid = 12
  Slack = 13
  Square = 14
  PrivateKey = 15
  Stripe = 16
  URI = 17
  Dropbox = 18
  Heroku = 19
  Mailchimp = 20
  Okta = 21
  OneLogin = 22
  PivotalTracker = 23
  SquareApp = 25
  Twilio = 26
  Test = 27
  TravisCI = 29
  SlackWebhook = 30
  PaypalOauth = 31
  PagerDutyApiKey = 32
  Firebase = 33
  Mailgun = 34
  HubSpot = 35
  GitHubApp = 36
  CircleCI = 37
  WpEngine = 38
  DatadogToken = 39
  FacebookOAuth = 40
  AsanaPersonalAccessToken = 41
  AmplitudeApiKey = 42
  BitLyAccessToken = 43
  CalendlyApiKey = 44
  ZapierWebhook = 45
  YoutubeApiKey = 46
  SalesforceOauth2 = 47
  TwitterApiSecret = 48
  NpmToken = 49
  NewRelicPersonalApiKey = 50
  AirtableApiKey = 51
  AkamaiToken = 52
  AmazonMWS = 53
  KubeConfig = 54
  Auth0oauth = 55
  Bitfinex = 56
  Clarifai = 57
  CloudflareGlobalApiKey = 58
  CloudflareCaKey = 59
  Confluent = 60
  ContentfulDelivery = 61
  DatabricksToken = 62
  DigitalOceanSpaces = 63
  DigitalOceanToken = 64
  DiscordBotToken = 65
  DiscordWebhook = 66
  EtsyApiKey = 67
  FastlyPersonalToken = 68
  GoogleOauth2 = 69
  ReCAPTCHA = 70 
  GoogleApiKey = 71
  Hunter = 72
  IbmCloudUserKey = 73
  Netlify = 74
  Vonage = 75
  EquinixOauth = 76
  Paystack = 77
  PlaidToken = 78
  PlaidKey = 79
  Plivo = 80
  Postmark = 81
  PubNubPublishKey = 82
  PubNubSubscriptionKey = 83
  PusherChannelKey = 84
  ScalewayKey = 85
  SendinBlueV2 = 86
  SentryToken = 87
  ShodanKey = 88
  SnykKey = 89
  SpotifyKey = 90
  TelegramBotToken = 91
  TencentCloudKey = 92
  TerraformCloudPersonalToken = 93
  TrelloApiKey = 94
  ZendeskApi = 95
  MaxMindLicense = 96
  AirtableMetadataApiKey = 97
  AsanaOauth = 98
  RapidApi = 99
  CloudflareApiToken = 100
  Webex = 101
  FirebaseCloudMessaging = 102
  ContentfulPersonalAccessToken = 103
  MapBox = 104
  MailJetBasicAuth = 105
  MailJetSMS = 106
  HubSpotApiKey = 107
  HubSpotOauth = 108
  SslMate = 109
  Auth0ManagementApiToken = 110
  MessageBird = 111
  ElasticEmail = 112
  FigmaPersonalAccessToken = 113
  MicrosoftTeamsWebhook = 114
  GitHubOld = 115
  VultrApiKey = 116
  Pepipost = 117
  Postman = 118
  CloudsightKey = 119
  JiraToken = 120
  NexmoApiKey = 121
  SegmentApiKey = 122
  SumoLogicKey = 123
  PushBulletApiKey = 124
  AirbrakeProjectKey = 125
  AirbrakeUserKey = 126
  PendoIntegrationKey = 127
  SplunkOberservabilityToken  = 128
  LokaliseToken = 129
  Calendarific = 130
  Jumpcloud = 131
  IpStack = 133
  Notion = 134
  DroneCI = 135
  AdobeIO = 136
  TwelveData = 137
  D7Network = 138
  ScrapingBee = 139
  KeenIO = 140
  Wakatime = 141
  Buildkite = 142
  Verimail = 143
  Zerobounce = 144
  Mailboxlayer = 145
  Fastspring = 146
  Paddle = 147
  Sellfy = 148
  FixerIO = 149
  ButterCMS = 150
  Taxjar = 151
  Avalara = 152
  Helpscout = 153
  ElasticPath = 154
  Zeplin = 155
  Intercom = 156
  Mailmodo = 157
  CannyIo = 158
  Pipedrive = 159
  Vercel = 160
  PosthogApp = 161
  SinchMessage = 162
  Ayrshare = 163
  HelpCrunch = 164
  LiveAgent = 165
  Beamer = 166
  WeChatAppKey = 167
  LineMessaging = 168
  UberServerToken = 169
  AlgoliaAdminKey = 170
  FullContact = 171
  Mandrill = 172
  Flutterwave = 173
  MattermostPersonalToken = 174
  Cloudant = 175
  LineNotify = 176
  LinearAPI = 177
  Ubidots = 178
  Anypoint = 179
  Dwolla = 180
  ArtifactoryAccessToken = 181
  Surge = 182
  Sparkpost = 183
  GoCardless = 184
  Codacy = 185
  Kraken = 186
  Checkout = 187
  Kairos = 188
  ClockworkSMS = 189
  Atlassian = 190
  LaunchDarkly = 191
  Coveralls = 192
  Linode = 193
  WePay = 194
  PlanetScale = 195
  Doppler = 196
  Agora = 197
  Samsara = 198
  FrameIO = 199
  RubyGems = 200
  OpenAI = 201
  SurveySparrow = 202
  Simvoly = 203
  Survicate = 204
  Omnisend = 205
  Groovehq = 206
  Newsapi = 207
  Chatbot = 208
  ClickSendsms = 209
  Getgist = 210
  CustomerIO = 211
  ApiDeck = 212
  Nftport = 213
  Copper = 214
  Close = 215
  Myfreshworks = 216
  Salesflare = 217
  Webflow = 218
  Duda = 219
  Yext = 220
  ContentStack = 221
  Storyblok = 222
  GraphCMS = 223
  Checkmarket = 224
  Convertkit = 225
  CustomerGuru = 226
  Kaleyra = 227
  Mailerlite = 228
  Qualaroo = 229
  SatismeterProjectkey = 230
  SatismeterWritekey = 231
  Simplesat = 232
  SurveyAnyplace = 233
  SurveyBot = 234
  Webengage = 235
  ZonkaFeedback = 236
  Delighted = 237
  Feedier = 238
  Abbysale = 239
  Magnetic = 240
  Nytimes = 241
  Polygon = 242
  Powrbot = 243
  ProspectIO = 244
  Skrappio = 245
  Monday = 246
  Smartsheets = 247
  Wrike = 248
  Float = 249
  Imagekit = 250
  Integromat = 251
  Salesblink = 252
  Bored = 253
  Campayn = 254
  Clinchpad = 255
  CompanyHub = 256
  Debounce = 257
  Dyspatch = 258
  Guardianapi = 259
  Harvest = 260
  Moosend = 261
  OpenWeather = 262
  Siteleaf = 263
  Squarespace = 264
  FlowFlu = 265
  Nimble = 266
  LessAnnoyingCRM = 267
  Nethunt = 268
  Apptivo = 269
  CapsuleCRM = 270
  Insightly = 271
  Kylas = 272
  OnepageCRM = 273
  User = 274
  ProspectCRM = 275
  ReallySimpleSystems = 276
  Airship = 277
  Artsy = 278
  Yandex = 279
  Clockify = 280
  Dnscheck = 281
  EasyInsight = 282
  Ethplorer = 283
  Everhour = 284
  Fulcrum = 285
  GeoIpifi = 286
  Jotform = 287
  Refiner = 288
  Timezoneapi = 289
  TogglTrack = 290
  Vpnapi = 291
  Workstack = 292
  Apollo = 293
  Eversign = 294
  Juro = 295
  KarmaCRM = 296
  Metrilo = 297
  Pandadoc = 298
  RevampCRM = 299
  Salescookie = 300
  Alconost = 301
  Blogger = 302
  Accuweather = 303
  Opengraphr = 304
  Rawg = 305
  Riotgames = 306
  RoninApp = 307
  Stormglass = 308
  Tomtom = 309
  Twitch = 310
  Documo = 311
  Cloudways = 312
  Veevavault = 313
  KiteConnect = 314
  ShopeeOpenPlatform = 315
  TeamViewer = 316
  Bulbul = 317
  CentralStationCRM = 318
  Teamgate = 319
  Axonaut = 320
  Tyntec = 321
  Appcues = 322
  Autoklose = 323
  Cloudplan = 324
  Dotmailer = 325
  GetEmail = 326
  GetEmails = 327
  Kontent = 328
  Leadfeeder = 329
  Raven = 330
  RocketReach = 331
  Uplead = 332
  Brandfetch = 333
  Clearbit = 334
  Crowdin = 335
  Mapquest = 336
  Noticeable = 337
  Onbuka = 338
  Todoist = 339
  Storychief = 340
  LinkedIn = 341
  YouSign = 342
  Docker = 343
  Telesign = 344
  Spoonacular = 345
  Aerisweather = 346
  Alphavantage = 347
  Imgur = 348
  Imagga = 349
  SMSApi = 350
  Distribusion = 351
  Blablabus = 352
  WordsApi = 353
  Currencylayer = 354
  Html2Pdf = 355
  IPGeolocation = 356
  Owlbot = 357
  Cloudmersive = 358
  Dynalist = 359
  ExchangeRateAPI = 360
  HolidayAPI = 361
  Ipapi = 362
  Marketstack = 363
  Nutritionix = 364
  Swell = 365
  ClickupPersonalToken = 366
  Nitro = 367
  Rev = 368
  RunRunIt = 369
  Typeform = 370
  Mixpanel = 371
  Tradier = 372
  Verifier = 373
  Vouchery = 374
  Alegra = 375
  Audd = 376
  Baremetrics = 377
  Coinlib = 378
  ExchangeRatesAPI = 379
  CurrencyScoop = 380
  FXMarket = 381
  CurrencyCloud = 382
  GetGeoAPI = 383
  Abstract = 384
  Billomat = 385
  Dovico = 386
  Bitbar = 387
  Bugsnag = 388
  AssemblyAI = 389
  AdafruitIO = 390
  Apify = 391
  CoinGecko = 392
  CryptoCompare = 393
  Fullstory = 394
  HelloSign = 395
  Loyverse = 396
  NetCore = 397
  SauceLabs = 398
  AlienVault = 399
  Apiflash = 401
  Coinlayer = 402
  CurrentsAPI = 403
  DataGov = 404
  Enigma = 405
  FinancialModelingPrep = 406
  Geocodio = 407
  HereAPI = 408
  Macaddress = 409
  OOPSpam = 410
  ProtocolsIO = 411
  ScraperAPI = 412
  SecurityTrails = 413
  TomorrowIO = 414
  WorldCoinIndex = 415
  FacePlusPlus = 416
  Voicegain = 417
  Deepgram = 418
  VisualCrossing = 419
  Finnhub = 420
  Tiingo = 421
  RingCentral = 422
  Finage = 423
  Edamam = 424
  HypeAuditor = 425
  Gengo = 426
  Front = 427
  Fleetbase = 428
  Bubble = 429
  Bannerbear = 430
  Adzuna = 431
  BitcoinAverage = 432
  CommerceJS = 433
  DetectLanguage = 434
  FakeJSON = 435
  Graphhopper = 436
  Lexigram = 437
  LinkPreview = 438
  Numverify = 439
  ProxyCrawl = 440
  ZipCodeAPI = 441
  Cometchat = 442
  Keygen = 443
  Mixcloud = 444
  TatumIO = 445
  Tmetric = 446
  Lastfm = 447
  Browshot = 448
  JSONbin = 449
  LocationIQ = 450
  ScreenshotAPI = 451
  WeatherStack = 452
  Amadeus = 453
  FourSquare = 454
  Flickr = 455
  ClickHelp = 456
  Ambee = 457
  Api2Cart = 458
  Hypertrack = 459
  KakaoTalk = 460
  RiteKit = 461
  Shutterstock = 462
  Text2Data = 463
  YouNeedABudget = 464
  Cricket = 465
  Filestack = 466
  Gyazo = 467
  Mavenlink = 468
  Sheety = 469
  Sportsmonk = 470
  Stockdata = 471
  Unsplash = 472
  Allsports = 473
  CalorieNinja = 474
  WalkScore = 475
  Strava = 476
  Cicero = 477
  IPQuality = 478
  ParallelDots = 479
  Roaring = 480
  Mailsac = 481
  Whoxy = 482
  WorldWeather = 483
  ApiFonica = 484
  Aylien = 485
  Geocode = 486
  IconFinder = 487
  Ipify = 488
  LanguageLayer = 489
  Lob = 490
  OnWaterIO = 491
  Pastebin = 492
  PdfLayer = 493
  Pixabay = 494
  ReadMe = 495
  VatLayer = 496
  VirusTotal = 497
  AirVisual = 498
  Currencyfreaks = 499
  Duffel = 500
  FlatIO = 501
  M3o = 502
  Mesibo = 503
  Openuv = 504
  Snipcart = 505
  Besttime = 506
  Happyscribe = 507
  Humanity = 508
  Impala = 509
  Loginradius = 510
  AutoPilot = 511
  Bitmex = 512
  ClustDoc = 513
  Messari = 514
  PdfShift = 515
  Poloniex = 516
  RestpackHtmlToPdfAPI = 517
  RestpackScreenshotAPI = 518
  ShutterstockOAuth = 519
  SkyBiometry = 520
  AbuseIPDB = 521
  AletheiaApi = 522
  BlitApp = 523
  Censys = 524
  Cloverly = 525
  CountryLayer = 526
  FileIO = 527
  FlightApi = 528
  Geoapify = 529
  IPinfoDB = 530
  MediaStack = 531
  NasdaqDataLink = 532
  OpenCageData = 533
  Paymongo = 534
  PositionStack = 535
  Rebrandly = 536
  ScreenshotLayer = 537
  Stytch = 538
  Unplugg = 539
  UPCDatabase = 540
  UserStack = 541
  Geocodify = 542
  Newscatcher = 543
  Nicereply = 544
  Partnerstack = 545
  Route4me = 546
  Scrapeowl = 547
  ScrapingDog = 548
  Streak = 549
  Veriphone = 550
  Webscraping = 551
  Zenscrape = 552
  Zenserp = 553
  CoinApi = 554
  Gitter = 555
  Host = 556
  Iexcloud = 557
  Restpack = 558
  ScraperBox = 559
  ScrapingAnt = 560
  SerpStack = 561
  SmartyStreets = 562
  TicketMaster = 563
  AviationStack = 564
  BombBomb = 565
  Commodities = 566
  Dfuse = 567
  EdenAI = 568
  Glassnode = 569
  Guru = 570
  Hive = 571
  Hiveage = 572
  Kickbox = 573
  Passbase = 574
  PostageApp = 575
  PureStake = 576
  Qubole = 577
  CarbonInterface = 578
  Intrinio = 579
  QuickMetrics = 580
  ScrapeStack = 581
  TechnicalAnalysisApi = 582
  Urlscan = 583
  BaseApiIO = 584
  DailyCO = 585
  TLy = 586
  Shortcut = 587
  Appfollow = 588
  Thinkific = 589
  Feedly = 590
  Stitchdata = 591
  Fetchrss = 592
  Signupgenius = 593
  Signaturit = 594
  Optimizely = 595
  OcrSpace = 596
  WeatherBit = 597
  BuddyNS = 598
  ZipAPI = 599
  ZipBooks = 600
  Onedesk = 601
  Bugherd = 602
  Blazemeter = 603
  Autodesk = 604
  Tru = 605
  UnifyID = 606
  Trimble = 607
  Smooch = 608
  Semaphore = 609
  Telnyx = 610
  Signalwire = 611
  Textmagic = 612
  Serphouse = 613
  Planyo = 614
  Simplybook = 615
  Vyte = 616
  Nylas = 617
  Squareup = 618
  Dandelion = 619
  DataFire = 620
  DeepAI = 621
  MeaningCloud = 622
  NeutrinoApi = 623
  Storecove = 624
  Shipday = 625
  Sentiment = 626
  StreamChatMessaging = 627
  TeamworkCRM = 628
  TeamworkDesk = 629
  TeamworkSpaces = 630
  TheOddsApi = 631
  Apacta = 632
  GetSandbox = 633
  Happi = 634
  Oanda = 635
  FastForex = 636
  APIMatic = 637
  VersionEye = 638
  EagleEyeNetworks = 639
  ThousandEyes = 640
  SelectPDF = 641
  Flightstats = 642
  ChecIO = 643
  Manifest = 644
  ApiScience = 645
  AppSynergy = 646
  Caflou = 647
  Caspio = 648
  ChecklyHQ = 649
  CloudElements = 650
  DronaHQ = 651
  Enablex = 652
  Fmfw = 653
  GoodDay = 654
  Luno = 655
  Meistertask = 656
  Mindmeister = 657
  PeopleDataLabs = 658
  ScraperSite = 659
  Scrapfly = 660
  SimplyNoted = 661
  TravelPayouts = 662
  WebScraper = 663
  Convier = 664
  Courier = 665
  Ditto = 666
  Findl = 667
  Lendflow = 668
  Moderation = 669
  Opendatasoft = 670
  Podio = 671
  Rockset = 672
  Rownd = 673
  Shotstack = 674
  Swiftype = 675
  Twitter = 676
  Honey = 677
  Freshdesk = 678
  Upwave = 679
  Fountain = 680
  Freshbooks = 681
  Mite = 682
  Deputy = 683
  Beebole = 684
  Cashboard = 685
  Kanban = 686
  Worksnaps = 687
  MyIntervals = 688
  InvoiceOcean = 689
  Sherpadesk = 690
  Mrticktock = 691
  Chatfule = 692
  Aeroworkflow = 693
  Emailoctopus = 694
  Fusebill = 695
  Geckoboard = 696
  Gosquared = 697
  Moonclerk = 698
  Paymoapp = 699
  Mixmax = 700
  Processst = 701
  Repairshopr  = 702
  Goshippo = 703
  Sigopt = 704
  Sugester = 705
  Viewneo = 706 
  BoostNote = 707
  CaptainData = 708
  Checkvist = 709
  Cliengo = 710
  Cloze = 711
  FormIO = 712
  FormBucket = 713
  GoCanvas = 714
  MadKudu = 715
  NozbeTeams = 716
  Papyrs = 717
  SuperNotesAPI = 718
  Tallyfy = 719
  ZenkitAPI = 720
  CloudImage = 721
  UploadCare = 722
  Borgbase = 723
  Pipedream = 724
  Sirv = 725
  Diffbot = 726
  EightxEight = 727
  Sendoso = 728
  Printfection = 729
  Authorize = 730
  PandaScore = 731
  Paymo = 732
  AvazaPersonalAccessToken = 733
  PlanviewLeanKit = 734
  Livestorm = 735
  KuCoin = 736
  MetaAPI = 737
  NiceHash = 738
  CexIO = 739
  Klipfolio = 740
  Dynatrace = 741
  MollieAPIKey = 742
  MollieAccessToken = 743
  BasisTheory = 744
  Nordigen = 745
  FlagsmithEnvironmentKey = 746
  FlagsmithToken = 747
  Mux = 748
  Column = 749
  Sendbird = 750
  SendbirdOrganizationAPI = 751
  Midise = 752
  Mockaroo = 753
  Image4 = 754
  Pinata = 755
  BrowserStack = 756
  CrossBrowserTesting = 757
  Loadmill = 758
  TestingBot = 759
  KnapsackPro = 760
  Qase = 761
  Dareboost = 762
  GTMetrics = 763
  Holistic = 764
  Parsers = 765
  ScrutinizerCi = 766
  SonarCloud = 767
  APITemplate = 768
  ConversionTools = 769
  CraftMyPDF = 770
  ExportSDK = 771
  GlitterlyAPI = 772
  Hybiscus = 773
  Miro = 774
  Statuspage = 775
  Statuspal = 776
  Teletype = 777
  TimeCamp = 778
  Userflow = 779
  Wistia = 780
  SportRadar = 781
  UptimeRobot = 782
  Codequiry = 783
  ExtractorAPI = 784
  Signable = 785
  MagicBell = 786
  Stormboard = 787
  Apilayer = 788
  Disqus = 789
  Woopra = 790
  Paperform =791
  Gumroad = 792
  Paydirtyapp = 793
  Detectify = 794
  Statuscake = 795
  Jumpseller = 796
  LunchMoney = 797
  Rosette = 798
  Yelp = 799
  Atera = 800
  EcoStruxureIT = 801
  Aha = 802
  Parsehub = 803
  PackageCloud = 804
  Cloudsmith = 805
  Flowdash = 806
  Flowdock = 807
  Fibery = 808
  Typetalk = 809
  VoodooSMS = 810
  ZulipChat = 811
  Formcraft = 812
  Iexapis = 813
  Reachmail = 814
  Chartmogul = 815
  Appointed = 816
  Wit = 817
  RechargePayments = 818

class ProcessResult(object):
    def __init__(self, repo, status, message, findings = []):
        self.repo = repo
        self.status = status
        self.message = message
        self.findings = findings
    def __repr__(self):
        if self.status == "SUCCESS":
            return f"{self.status}::{self.repo.name}::{self.message}::{len(self.findings)}"
        else:
            return f"{self.status}::{self.repo.name}::{self.message}"

def get_branches(path):
    r = Repo.init(path)
    return list([x.remote_head for x in r.remotes[0].refs if x.is_detached == True])

def process_repo(repo, pat, functions):
    out = []
    try:
        path = clone_repo(repo.clone_url,pat)
    except:
        return [ProcessResult(repo, "FAIL", "Could not clone")]
    for branch in get_branches(path):
        # print(branch)
        # Repo.init(path).git.checkout(branch,"--")
        for function in functions:
            try:
                out.append(ProcessResult(repo, "SUCCESS", function.__name__, function(path, repo, branch)))
            except:
                out.append(ProcessResult(repo, "FAIL", f"Could not {function.__name__}"))
    for i in range(3):
        try:
            rmtree(path, onerror=onerror)
            break
        except:
            sleep(10)
            pass
    ret = []
    for function in functions:
        deduped = {}
        for result in out:
            if result.status != "SUCCESS":
                ret.append(result)
            if result.status == "SUCCESS" and result.message == function.__name__:
                for f in result.findings:
                    key = f"{f.commit}{f.file}{f.line}{f.hashed_secret}"
                    deduped[key] = f
        ret.append(ProcessResult(repo, "SUCCESS", function.__name__, deduped.values()))
    return ret

class Finding(object):
    def __init__(self,
                    source,
                    detector_type,
                    verified,
                    commit,
                    date,
                    author_email,
                    repository,
                    repository_uri,
                    link,
                    secret,
                    file,
                    line,
                    redacted_secret = None
                    ):
        self.source = source
        self.detector_type = detector_type 
        self.verified = verified
        self.commit = commit
        self.date = date
        self.author_email = author_email
        self.repository = repository
        self.repository_uri = repository_uri
        self.link = link
        self.file = file
        self.line = line
        self.filename = file.split("/")[-1]
        self.extension =  file.split(".")[-1] if '.' in file else ""
        self.hashed_secret = sha256(secret.encode('utf-8')).hexdigest()
        if redacted_secret == None:
            self.redacted_secret = self.redact(secret)
    def redact(self,secret):
        #TODO: redact and persist secret on another property
        return secret
        if len(secret) < 5:
            return "REDACTED"
        else:
            return f"{secret[0:3]}{'*' * (len(secret) - 4)}"    
    
    @staticmethod
    def fromTrufflehog(trufflehog_dict, repo):
        data = trufflehog_dict["SourceMetadata"]["Data"]
        commit = "master" if data["Git"]["commit"] == "unstaged" else data["Git"]["commit"]
        return Finding(
                    source = "trufflehog",
                    detector_type = DetectorTypeEnum(trufflehog_dict["DetectorType"]).name,
                    verified = trufflehog_dict["Verified"],
                    commit = commit,
                    date = data["Git"]["timestamp"],
                    author_email = data["Git"]["email"],
                    repository = repo.name,
                    repository_uri = data["Git"]["repository"],
                    link = f"{repo.html_url}/blob/{commit}/{data['Git']['file']}",
                    secret = b64decode(trufflehog_dict["Raw"]).decode('utf-8'),
                    file = data["Git"]["file"],
                    line = data["Git"]["line"],
        )
    
    @staticmethod
    def fromGitLeak(gitleak_dict, repo):
        repo_url = repo.html_url
        link = f"{repo.html_url}/blob/{gitleak_dict['Commit']}/{gitleak_dict['File']}"
        return Finding(
                    source = "gitleaks",
                    detector_type = gitleak_dict["RuleID"],
                    verified = False,
                    commit = gitleak_dict["Commit"],
                    date = gitleak_dict["Date"],
                    author_email = gitleak_dict["Email"],
                    repository = repo.name,
                    repository_uri = repo_url,
                    link = link,
                    secret = gitleak_dict["Secret"],
                    file = gitleak_dict["File"],
                    line = gitleak_dict["StartLine"],
        )

    def __repr__(self):
        return f"{self.hashed_secret}:{self.repository}:{self.file}"

def truffle_hog(path, repo, branch=None):
    target = f"file://{path}"
    truffle_hog = ["trufflehog","--no-update", "--json","git", target, "--no-verification", "--fail"]
    if branch != None:
        truffle_hog.append(f"--branch={branch}")
    output = run(truffle_hog, capture_output = True)
    if output.returncode == 0:
        return []
    ret = []
    for line in output.stdout.decode('utf-8').split("\n"):
        if line == "":
            continue
        f = Finding.fromTrufflehog(loads(line), repo)
        ret.append(f)
    return ret

def gitleaks(path, repo, branch=None):
    temp_path = f"{path}.out"
    gitleaks = ["gitleaks","detect", "-s", path, "-r", temp_path]
    if branch != None:
        gitleaks.append(f"--log-opts={branch}")
    result = run(gitleaks, capture_output = True)
    if result.returncode == 1:
        try:
            with open(temp_path, "r") as f:
                findings = f.read()
        except:
            return []
        findings_list = loads(findings)
        ret = []
        for finding_dict in findings_list:
            ret.append(Finding.fromGitLeak(finding_dict,repo))
        remove(temp_path)
        return ret
    else:
        try:
            remove(temp_path)
        except:
            pass
        return []


if __name__ == '__main__':
    #TODO: arg parse
    g = Github(api_token)
    repos = g.get_organization(organisation).get_repos()
    total_results = []
    f = partial(process_repo, pat=api_token, functions=[gitleaks, truffle_hog])
    pool = ThreadPool(parallelism)
    results = pool.imap_unordered(f, repos)
    with open('results.json', 'w', 1, encoding='utf-8') as f:
        for result_batch in results:
            for result in result_batch:
                print(result)
                if result.status == "FAIL" or result.findings == []:
                    continue
                for item in result.findings:
                    total_results.append(item)
                    f.write(f"{item.__dict__}\n")

