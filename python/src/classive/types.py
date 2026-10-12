# Generated from schema/openapi.json by scripts/generate.mjs. Do not edit.
from typing import Any, Literal, NotRequired, TypedDict, Union, TypeAlias

class Audience(TypedDict):
    band: Literal["primary", "lower-secondary", "upper-secondary", "university", "adult"]
    grade: NotRequired[str]
    priorKnowledge: NotRequired[list[str]]
    depth: NotRequired[Literal["foundational", "standard", "rigorous"]]
    purpose: NotRequired[str]
    language: NotRequired[str]
    locale: NotRequired[str]
    curriculum: NotRequired[str]
    examBoard: NotRequired[str]

class Preferences(TypedDict):
    video: NotRequired[str]
    captions: NotRequired[str]
    notes: NotRequired[str]

Metadata: TypeAlias = dict[str, str]

class CreateClip(TypedDict):
    type: Literal["clip"]
    prompt: str
    goals: NotRequired[list[str]]
    audience: "Audience"
    materials: NotRequired[list[str]]
    preferences: NotRequired["Preferences"]
    metadata: NotRequired["Metadata"]
    outputs: NotRequired[list[Literal["video", "notes", "quiz", "flashcards"]]]
    voice: NotRequired[Literal["adam", "patrick", "alice", "daniel", "lily", "george", "matilda", "bella", "chris", "eric", "sarah", "river"]]
    lengthMinutes: NotRequired[int]
    basedOn: NotRequired[str]
    research: NotRequired["Research"]
    assessment: NotRequired["Assessment"]
    quoteId: NotRequired[str]

class CreateLesson(TypedDict):
    type: Literal["lesson"]
    prompt: str
    goals: NotRequired[list[str]]
    audience: "Audience"
    materials: NotRequired[list[str]]
    preferences: NotRequired["Preferences"]
    metadata: NotRequired["Metadata"]
    outputs: NotRequired[list[Literal["video", "notes", "quiz", "flashcards"]]]
    voice: NotRequired[Literal["adam", "patrick", "alice", "daniel", "lily", "george", "matilda", "bella", "chris", "eric", "sarah", "river"]]
    lengthMinutes: NotRequired[int]
    basedOn: NotRequired[str]
    research: NotRequired["Research"]
    assessment: NotRequired["Assessment"]
    quoteId: NotRequired[str]

class CreateCourse(TypedDict):
    type: Literal["course"]
    prompt: str
    goals: NotRequired[list[str]]
    audience: "Audience"
    materials: NotRequired[list[str]]
    preferences: NotRequired["Preferences"]
    metadata: NotRequired["Metadata"]
    outputs: NotRequired[list[Literal["video", "notes", "quiz", "flashcards"]]]
    voice: NotRequired[Literal["adam", "patrick", "alice", "daniel", "lily", "george", "matilda", "bella", "chris", "eric", "sarah", "river"]]
    title: NotRequired[str]
    lessons: NotRequired[int]
    research: NotRequired["Research"]
    assessment: NotRequired["Assessment"]
    quoteId: NotRequired[str]
    lengthMinutes: NotRequired[int]
    totalMinutes: NotRequired[int]

class CreateReview(TypedDict):
    type: Literal["review"]
    prompt: NotRequired[str]
    goals: NotRequired[list[str]]
    audience: "Audience"
    materials: list[str]
    preferences: NotRequired["Preferences"]
    metadata: NotRequired["Metadata"]
    research: NotRequired["Research"]
    assessment: NotRequired["Assessment"]
    quoteId: NotRequired[str]

CreateJobRequest: TypeAlias = Union["CreateClip", "CreateLesson", "CreateReview"]

AcceptedJobInput: TypeAlias = Union["CreateClip", "CreateLesson", "CreateCourse", "CreateReview"]

class CreateRevisionRequest(TypedDict):
    prompt: str
    quoteId: NotRequired[str]

class FileRef(TypedDict):
    id: str
    url: str
    contentType: str
    bytes: int
    durationSeconds: NotRequired[float]

class LessonResult(TypedDict):
    order: int
    title: Union[str, None]
    video: NotRequired["FileRef"]
    captions: NotRequired["LessonResultCaptions"]
    notes: NotRequired["LessonResultNotes"]
    quiz: NotRequired["FileRef"]
    flashcards: NotRequired["FileRef"]
    thumbnail: NotRequired["FileRef"]

class JobResults(TypedDict):
    lessons: list["LessonResult"]
    review: NotRequired["FileRef"]

class Job(TypedDict):
    id: str
    object: Literal["job"]
    type: Literal["clip", "lesson", "course", "review"]
    status: Literal["queued", "processing", "cancelling", "cancelled", "completed", "failed"]
    input: "AcceptedJobInput"
    createdAt: Union[str, None]
    startedAt: Union[str, None]
    completedAt: Union[str, None]
    estimatedCompletionAt: Union[str, None]
    progress: NotRequired["JobProgress"]
    basedOn: NotRequired[str]
    revisionOf: NotRequired[str]
    credits: "JobCredits"
    results: NotRequired["JobResults"]
    failure: NotRequired["JobFailure"]
    curriculum: NotRequired["JobCurriculum"]
    lessons: NotRequired[list["JobLessonsItem"]]
    package: NotRequired["JobPackage"]
    sourceCoverage: NotRequired["SourceCoverage"]
    curriculumReview: NotRequired["CurriculumReview"]
    parentJobId: NotRequired[str]
    lessonId: NotRequired[str]
    courseOrigin: NotRequired["JobCourseOrigin"]
    retryOf: NotRequired[str]
    learningGoals: NotRequired[list["JobLearningGoalsItem"]]

class JobList(TypedDict):
    object: Literal["list"]
    data: list["Job"]
    hasMore: bool

class Estimate(TypedDict):
    object: Literal["estimate"]
    credits: int
    includesQualityReview: NotRequired[Literal[False]]
    requiresQuote: NotRequired[Literal[True]]
    outputs: list[Literal["video", "notes", "quiz", "flashcards", "review"]]
    balance: int

class Usage(TypedDict):
    object: Literal["usage"]
    job: str
    credits: "UsageCredits"
    stages: list["UsageStagesItem"]

class Material(TypedDict):
    id: str
    object: Literal["material"]
    filename: str
    contentType: Literal["application/pdf", "text/plain", "text/markdown", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    bytes: int
    characters: int
    truncated: bool
    createdAt: str
    status: Literal["queued", "processing", "ready", "failed", "deleted"]
    version: int
    previousVersionId: NotRequired[Union[str, None]]
    role: NotRequired[Literal["syllabus", "reference", "assessment"]]
    sourceUrl: NotRequired[Union[str, None]]
    rights: NotRequired[Union[str, None]]
    coverage: "MaterialCoverage"
    error: NotRequired[str]
    sections: list["MaterialSection"]
    retention: NotRequired["MaterialRetention"]

class MaterialList(TypedDict):
    object: Literal["list"]
    data: list["Material"]
    hasMore: NotRequired[bool]
    nextCursor: NotRequired[Union[str, None]]

class MaterialUpload(TypedDict):
    filename: str
    contentType: Literal["application/pdf", "text/plain", "text/markdown", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    base64: str
    previousVersionId: NotRequired[str]
    role: NotRequired[Literal["syllabus", "reference", "assessment"]]
    sourceUrl: NotRequired[str]
    rights: NotRequired[str]
    retentionDays: NotRequired[int]

class Voice(TypedDict):
    id: Literal["adam", "patrick", "alice", "daniel", "lily", "george", "matilda", "bella", "chris", "eric", "sarah", "river"]
    name: str
    accent: Literal["american", "british", "neutral"]
    gender: Literal["female", "male", "neutral"]
    description: str
    previewUrl: str

class VoiceList(TypedDict):
    object: Literal["list"]
    data: list["Voice"]

class PreferenceExamples(TypedDict):
    video: list[str]
    captions: list[str]
    notes: list[str]
    avoid: list[str]

class Prices(TypedDict):
    unit: Literal["credit"]
    creditValueUsd: float
    prices: "PricesPrices"

class ApiKey(TypedDict):
    id: str
    object: Literal["key"]
    name: str
    prefix: str
    createdAt: str
    lastUsedAt: Union[str, None]
    revokedAt: Union[str, None]
    kind: NotRequired[Literal["api", "mcp"]]
    scopes: NotRequired[list[Literal["read", "generate", "materials", "manage"]]]

class CreatedApiKey(TypedDict):
    id: str
    object: Literal["key"]
    name: str
    prefix: str
    createdAt: str
    lastUsedAt: Union[str, None]
    revokedAt: Union[str, None]
    key: str
    kind: NotRequired[Literal["api", "mcp"]]
    scopes: NotRequired[list[Literal["read", "generate", "materials", "manage"]]]

class ApiKeyList(TypedDict):
    object: Literal["list"]
    data: list["ApiKey"]

class CreateKeyRequest(TypedDict):
    name: NotRequired[str]
    kind: NotRequired[Literal["api", "mcp"]]
    scopes: NotRequired[list[Literal["read", "generate", "materials", "manage"]]]

class Webhook(TypedDict):
    id: str
    object: Literal["webhook"]
    url: str
    events: list[Literal["job.completed", "job.failed", "job.cancelled", "billing.low_balance", "billing.auto_topup_failed", "billing.auto_topup_paused", "billing.auto_topup_capped", "billing.topup_succeeded", "billing.payment_method_saved"]]
    createdAt: str

class CreatedWebhook(TypedDict):
    id: str
    object: Literal["webhook"]
    url: str
    events: list[Literal["job.completed", "job.failed", "job.cancelled", "billing.low_balance", "billing.auto_topup_failed", "billing.auto_topup_paused", "billing.auto_topup_capped", "billing.topup_succeeded", "billing.payment_method_saved"]]
    createdAt: str
    secret: str

class WebhookList(TypedDict):
    object: Literal["list"]
    data: list["Webhook"]

class CreateWebhookRequest(TypedDict):
    url: str
    events: NotRequired[list[Literal["job.completed", "job.failed", "job.cancelled", "billing.low_balance", "billing.auto_topup_failed", "billing.auto_topup_paused", "billing.auto_topup_capped", "billing.topup_succeeded", "billing.payment_method_saved"]]]

class LedgerEntry(TypedDict):
    kind: Literal["topup", "reserve", "release", "charge", "grant", "adjustment"]
    credits: int
    balanceAfter: int
    job: Union[str, None]
    topup: Union[str, None]
    createdAt: str

class Credits(TypedDict):
    object: Literal["credits"]
    balance: int
    creditValueUsd: float
    recent: list["LedgerEntry"]

class Packs(TypedDict):
    object: Literal["list"]
    creditValueUsd: float
    minimumUsd: int
    maximumUsd: int
    data: list["PacksDataItem"]

class CreateTopupRequest(TypedDict):
    amountUsd: int
    savePaymentMethod: NotRequired[bool]

class CreatedTopup(TypedDict):
    id: str
    object: Literal["topup"]
    credits: int
    amountUsd: int
    status: Literal["open"]
    paymentEnvironment: Literal["sandbox", "live"]
    checkoutUrl: str

class Topup(TypedDict):
    id: str
    object: Literal["topup"]
    credits: int
    amountUsd: float
    status: Literal["open", "paid", "expired", "failed"]
    paymentEnvironment: Literal["sandbox", "live", "unavailable"]
    paidAt: Union[str, None]

class Error(TypedDict):
    error: "ErrorError"

class WebhookEvent(TypedDict):
    id: str
    object: Literal["event"]
    type: Literal["job.completed", "job.failed", "job.cancelled", "billing.low_balance", "billing.auto_topup_failed", "billing.auto_topup_paused", "billing.auto_topup_capped", "billing.topup_succeeded", "billing.payment_method_saved"]
    createdAt: str
    data: Union["WebhookEventData0", "BillingEventData"]

class Figure(TypedDict):
    url: str
    caption: str

class NotesFile(TypedDict):
    markdown: str
    sections: list["NotesFileSectionsItem"]
    keyTerms: list["NotesFileKeyTermsItem"]

class QuizFile(TypedDict):
    questions: list["QuizFileQuestionsItem"]

class FlashcardsFile(TypedDict):
    cards: list["FlashcardsFileCardsItem"]

class ReviewFile(TypedDict):
    summary: str
    audienceFit: "ReviewFileAudienceFit"
    accuracy: list["ReviewFileAccuracyItem"]
    clarity: list["ReviewFileClarityItem"]
    coverage: "ReviewFileCoverage"
    suggestions: list[str]

class BillingPaymentMethod(TypedDict):
    id: str
    type: Literal["card"]
    brand: str
    last4: str
    expiresMonth: int
    expiresYear: int
    isDefault: bool
    disabled: bool

class BillingSettings(TypedDict):
    object: Literal["billing_settings"]
    alert: "BillingSettingsAlert"
    autoTopup: "BillingSettingsAutoTopup"
    paymentMethods: list["BillingPaymentMethod"]
    paymentEnvironment: Literal["sandbox", "live", "unavailable"]
    canSaveCard: bool
    canAutoTopup: bool
    availabilityReason: Union[str, None]
    alerts: list["BillingSettingsAlertsItem"]

class BillingSettingsPatch(TypedDict):
    alert: NotRequired["BillingSettingsPatchAlert"]
    autoTopup: NotRequired["BillingSettingsPatchAutoTopup"]

class CardSetup(TypedDict):
    id: str
    checkoutUrl: str

class BillingPortal(TypedDict):
    url: str

class UnlinkedPaymentMethod(TypedDict):
    id: str
    disabled: Literal[True]
    providerDeleted: Literal[False]

class BillingEventData(TypedDict):
    alert: NotRequired["BillingEventDataAlert"]
    balanceCredits: NotRequired[int]
    thresholdCredits: NotRequired[int]
    topup: NotRequired["BillingEventDataTopup"]
    paymentMethod: NotRequired["BillingEventDataPaymentMethod"]

class Research(TypedDict):
    web: NotRequired[bool]
    corpus: NotRequired[bool]

class Assessment(TypedDict):
    questions: NotRequired[int]
    types: NotRequired[list[Literal["multiple-choice", "short-answer", "true-false"]]]
    difficulty: NotRequired[Literal["accessible", "standard", "challenging"]]

class MaterialSection(TypedDict):
    id: str
    title: str
    start: int
    end: int
    chapterId: NotRequired[str]
    chapterTitle: NotRequired[str]
    page: NotRequired[int]
    pageEnd: NotRequired[int]
    summary: NotRequired[Union[str, None]]

class MaterialCoverage(TypedDict):
    complete: bool
    sections: int
    characters: int
    pages: NotRequired[int]
    coveredPages: NotRequired[list[int]]
    unlocatedPages: NotRequired[list[int]]
    locators: NotRequired[Literal["page", "character"]]

class CurriculumInput(TypedDict):
    prompt: str
    audience: "Audience"
    goals: NotRequired[list[str]]
    materials: NotRequired[list[str]]
    research: NotRequired["Research"]
    lessons: NotRequired[int]
    lengthMinutes: NotRequired[int]
    totalMinutes: NotRequired[int]
    standard: NotRequired["CurriculumInputStandard"]

class PlanLesson(TypedDict):
    id: str
    title: str
    module: str
    goals: list[str]
    prerequisites: list[str]
    lengthMinutes: int
    learningMinutes: int
    sourceSections: list[str]

class CurriculumPlan(TypedDict):
    title: str
    description: str
    lessons: list["PlanLesson"]
    gaps: list[str]
    sources: list["CurriculumPlanSourcesItem"]
    coverage: list["CurriculumPlanCoverageItem"]

class Curriculum(TypedDict):
    id: str
    object: Literal["curriculum"]
    version: int
    status: Literal["drafting", "draft", "approved", "failed"]
    input: "CurriculumInput"
    plan: Union["CurriculumPlan", None]
    error: Union[str, None]
    createdAt: str
    credits: "CurriculumCredits"
    changes: NotRequired["CurriculumChanges"]

class Quote(TypedDict):
    id: str
    object: Literal["quote"]
    credits: int
    expiresAt: str
    items: list["QuoteItemsItem"]
    input: dict[str, Any]
    fundedWork: NotRequired["QuoteFundedWork"]
    attempt: NotRequired["QuoteAttempt"]
    maximumChargeCredits: NotRequired[int]
    rates: NotRequired[dict[str, Any]]
    materialVersions: NotRequired[list["QuoteMaterialVersionsItem"]]
    researchAllowance: NotRequired["QuoteResearchAllowance"]
    costPolicy: NotRequired["QuoteCostPolicy"]

class Limits(TypedDict):
    maxConcurrentJobs: int
    dailyCredits: int

class CurriculumList(TypedDict):
    object: Literal["list"]
    data: list["Curriculum"]

class CurriculumRecommendation(TypedDict):
    basis: NotRequired[Literal["maintained-template"]]
    guidance: NotRequired[list[str]]
    id: str
    title: str
    description: str
    reason: str
    input: "CurriculumInput"
    plan: "CurriculumPlan"

class CurriculumRecommendationList(TypedDict):
    object: Literal["list"]
    data: list["CurriculumRecommendation"]

class DeletedMaterial(TypedDict):
    id: str
    object: Literal["material"]
    status: Literal["deleted"]

class Selection(TypedDict):
    version: int
    lessonIds: NotRequired[list[str]]
    outputs: NotRequired[list[Literal["video", "notes", "quiz", "flashcards"]]]
    voice: NotRequired[Literal["adam", "patrick", "alice", "daniel", "lily", "george", "matilda", "bella", "chris", "eric", "sarah", "river"]]
    assessment: NotRequired["Assessment"]

class Package(TypedDict):
    version: Literal[1]
    course: str
    audience: Literal["learner", "instructor"]
    curriculum: NotRequired["PackageCurriculum"]
    complete: bool
    createdAt: str
    lessons: list["PackageLessonsItem"]

class CurriculumReview(TypedDict):
    required: bool
    currentVersion: int
    changedPrerequisiteIds: list[str]

class SourceCoverage(TypedDict):
    scope: Literal["selected-passages", "whole-document-review"]
    materials: list["SourceCoverageMaterialsItem"]

class ListJobsQuery(TypedDict):
    limit: NotRequired[int]
    starting_after: NotRequired[str]

class ListMaterialsQuery(TypedDict):
    search: NotRequired[str]
    status: NotRequired[Literal["ready", "queued", "processing", "failed"]]
    limit: NotRequired[int]
    starting_after: NotRequired[str]

class CreateCurriculumInput(TypedDict):
    prompt: str
    audience: "Audience"
    goals: NotRequired[list[str]]
    materials: NotRequired[list[str]]
    research: NotRequired["Research"]
    lessons: NotRequired[int]
    lengthMinutes: NotRequired[int]
    totalMinutes: NotRequired[int]
    standard: NotRequired["CreateCurriculumInputStandard"]
    quoteId: str

class ImportCurriculumInput(TypedDict):
    input: "CurriculumInput"
    plan: "CurriculumPlan"

class GetCurriculumQuery(TypedDict):
    version: NotRequired[int]

class EditCurriculumInput(TypedDict):
    expectedVersion: int
    plan: "CurriculumPlan"

class ApproveCurriculumInput(TypedDict):
    version: int

class GenerateCurriculumLessonsInput(TypedDict):
    quoteId: str

class GetPackageQuery(TypedDict):
    audience: NotRequired[Literal["learner", "instructor"]]

class DownloadPackageQuery(TypedDict):
    audience: NotRequired[Literal["learner", "instructor"]]

class GetPackageFileQuery(TypedDict):
    audience: NotRequired[Literal["learner", "instructor"]]
    answers: NotRequired[bool]

class QuoteRevisionInput(TypedDict):
    prompt: str

class RetryJobInput(TypedDict):
    quoteId: str

class LessonResultCaptions(TypedDict):
    vtt: Union["FileRef", None]
    srt: Union["FileRef", None]

class LessonResultNotes(TypedDict):
    markdown: Union["FileRef", None]
    pdf: Union["FileRef", None]
    json: Union["FileRef", None]

class JobProgress(TypedDict):
    percent: Union[int, None]
    estimated: NotRequired[bool]
    stage: NotRequired[Literal["research", "writing", "evaluation", "checking", "correction", "visuals", "video", "finishing", "review"]]
    stages: list["JobProgressStagesItem"]

class JobCredits(TypedDict):
    reserved: int
    charged: int

class JobFailure(TypedDict):
    code: Literal["materials_unreadable", "content_not_suitable", "generation_failed", "render_failed", "review_rejected", "timed_out", "internal_error"]
    message: str

class JobCurriculum(TypedDict):
    id: str
    version: int

class JobLessonsItem(TypedDict):
    id: str
    title: str
    order: int
    jobId: str
    status: Literal["queued", "processing", "cancelling", "cancelled", "completed", "failed"]
    files: NotRequired["JobResults"]
    credits: "JobLessonsItemCredits"
    sourceCoverage: NotRequired["SourceCoverage"]
    curriculumReview: NotRequired["CurriculumReview"]

class JobPackage(TypedDict):
    manifest: str
    download: str

class JobCourseOrigin(TypedDict):
    parentJobId: str
    lessonId: str

class JobLearningGoalsItem(TypedDict):
    id: str
    text: str

class UsageCredits(TypedDict):
    reserved: int
    charged: int

class UsageStagesItem(TypedDict):
    stage: Literal["writing", "visuals", "voice", "rendering", "checks"]
    operations: int
    minutes: NotRequired[float]

class MaterialRetention(TypedDict):
    policy: Literal["until-deleted", "expires-after-days"]
    days: Union[int, None]
    expiresAt: Union[str, None]
    deletes: list[str]
    retains: list[str]

class PricesPrices(TypedDict):
    videoMinute: NotRequired[float]
    notes: NotRequired[float]
    quiz: NotRequired[float]
    flashcards: NotRequired[float]
    materialPer10kCharacters: NotRequired[float]
    review: NotRequired[float]
    reviewPer10kCharacters: NotRequired[float]
    defaultCourseLessons: NotRequired[float]
    courseLessonMinutes: NotRequired[float]

class PacksDataItem(TypedDict):
    amountUsd: int
    credits: int

class ErrorError(TypedDict):
    code: Literal["invalid_request", "unauthorized", "forbidden", "not_found", "conflict", "insufficient_credits", "too_large", "unsupported_media_type", "unprocessable", "rate_limited", "unavailable", "internal_error"]
    message: str
    details: NotRequired[list["ErrorErrorDetailsItem"]]

class WebhookEventData0(TypedDict):
    job: "WebhookEventData0Job"

class NotesFileSectionsItem(TypedDict):
    heading: str
    content: str
    level: int
    figure: NotRequired["Figure"]

class NotesFileKeyTermsItem(TypedDict):
    term: str
    definition: str

class QuizFileQuestionsItem(TypedDict):
    id: str
    type: str
    question: str
    options: NotRequired[list[str]]
    correctAnswer: Union[int, str]
    explanation: NotRequired[str]
    figure: NotRequired["Figure"]
    goalIds: NotRequired[list[str]]

class FlashcardsFileCardsItem(TypedDict):
    front: str
    back: str

class ReviewFileAudienceFit(TypedDict):
    fit: NotRequired[str]
    notes: NotRequired[str]

class ReviewFileAccuracyItem(TypedDict):
    quote: str
    issue: str
    suggestion: str
    severity: str

class ReviewFileClarityItem(TypedDict):
    quote: str
    issue: str
    suggestion: str

class ReviewFileCoverage(TypedDict):
    goals: list["ReviewFileCoverageGoalsItem"]

class BillingSettingsAlert(TypedDict):
    enabled: bool
    thresholdCredits: int

class BillingSettingsAutoTopup(TypedDict):
    enabled: bool
    thresholdCredits: int
    amountUsd: int
    monthlyMaximumUsd: int
    paymentMethodId: Union[str, None]
    monthlyUsedUsd: float
    status: Literal["off", "ready", "capped", "waiting", "paused"]
    lastError: Union[str, None]

class BillingSettingsAlertsItem(TypedDict):
    id: str
    type: str
    message: str
    createdAt: str

class BillingSettingsPatchAlert(TypedDict):
    enabled: NotRequired[bool]
    thresholdCredits: NotRequired[int]

class BillingSettingsPatchAutoTopup(TypedDict):
    enabled: NotRequired[bool]
    thresholdCredits: NotRequired[int]
    amountUsd: NotRequired[int]
    monthlyMaximumUsd: NotRequired[int]
    paymentMethodId: NotRequired[Union[str, None]]
    agree: NotRequired[Literal[True]]

class BillingEventDataAlert(TypedDict):
    id: str
    type: str
    message: str

class BillingEventDataTopup(TypedDict):
    id: str
    credits: int
    automatic: bool
    paymentEnvironment: Literal["sandbox", "live", "unavailable"]

class BillingEventDataPaymentMethod(TypedDict):
    id: str
    type: Literal["card"]
    brand: str
    last4: str

class CurriculumInputStandard(TypedDict):
    name: str
    edition: NotRequired[str]
    sourceUrl: NotRequired[str]

class CurriculumPlanSourcesItem(TypedDict):
    title: str
    url: NotRequired[str]

class CurriculumPlanCoverageItem(TypedDict):
    materialId: str
    sectionId: str
    lessonIds: list[str]

class CurriculumCredits(TypedDict):
    reserved: int
    charged: int

class CurriculumChanges(TypedDict):
    fromVersion: int
    changedLessonIds: list[str]
    affectedLessonIds: list[str]
    warnings: list["CurriculumChangesWarningsItem"]

class QuoteItemsItem(TypedDict):
    label: str
    credits: int

class QuoteFundedWork(TypedDict):
    providerBudgets: NotRequired["QuoteFundedWorkProviderBudgets"]
    fundingVersion: NotRequired[Literal["fixed-video-v1"]]
    fixedChargeCredits: NotRequired[int]
    preacceptanceBudgetUsd: NotRequired[float]
    qualityCredits: NotRequired[int]
    minimumChargeCredits: int
    modelBudgetUsd: float
    selectedMaterialCharacters: NotRequired[int]
    minimumVideoSeconds: NotRequired[float]
    admission: NotRequired["QuoteFundedWorkAdmission"]

class QuoteAttempt(TypedDict):
    operation: Literal["retry", "revision"]
    sourceJobId: str

class QuoteMaterialVersionsItem(TypedDict):
    id: str
    version: int

class QuoteResearchAllowance(TypedDict):
    web: bool
    corpus: bool
    budgetUsd: float

class QuoteCostPolicy(TypedDict):
    budgetUsd: float
    coverage: Literal["partial"]
    includes: list[str]
    estimated: list[str]
    unpriced: list[str]
    retries: Literal["share-the-budget"]

class PackageCurriculum(TypedDict):
    id: str
    version: int

class PackageLessonsItem(TypedDict):
    id: str
    order: int
    title: str
    jobId: str
    files: list["PackageLessonsItemFilesItem"]

class SourceCoverageMaterialsItem(TypedDict):
    materialId: str
    version: int
    extracted: "SourceCoverageMaterialsItemExtracted"
    selected: "SourceCoverageMaterialsItemSelected"
    omitted: "SourceCoverageMaterialsItemOmitted"
    covered: "SourceCoverageMaterialsItemCovered"
    reviewedSectionIds: list[str]

class CreateCurriculumInputStandard(TypedDict):
    name: str
    edition: NotRequired[str]
    sourceUrl: NotRequired[str]

class JobProgressStagesItem(TypedDict):
    stage: Literal["research", "writing", "evaluation", "checking", "correction", "visuals", "video", "finishing", "review"]
    status: Literal["waiting", "running", "done"]
    percent: Union[int, None]
    startedAt: NotRequired[str]
    completedAt: NotRequired[str]

class JobLessonsItemCredits(TypedDict):
    reserved: int
    charged: int

class ErrorErrorDetailsItem(TypedDict):
    field: NotRequired[str]
    message: str

class WebhookEventData0Job(TypedDict):
    id: str
    type: Literal["clip", "lesson", "course", "review"]
    status: Literal["completed", "failed", "cancelled"]
    failure: NotRequired["WebhookEventData0JobFailure"]

class ReviewFileCoverageGoalsItem(TypedDict):
    goal: str
    covered: bool
    where: NotRequired[str]

class CurriculumChangesWarningsItem(TypedDict):
    lessonId: str
    changedPrerequisiteIds: list[str]
    reason: Literal["prerequisite_changed"]

class QuoteFundedWorkProviderBudgets(TypedDict):
    version: Literal["bounded-providers-v1"]
    speech: "QuoteFundedWorkProviderBudgetsSpeech"
    imagesUsd: Literal[0]
    soundEffectsUsd: Literal[0]
    animationModelsUsd: Literal[0]
    visualCapabilityBuildsUsd: Literal[0]

class QuoteFundedWorkAdmission(TypedDict):
    admitted: bool
    requiredBudgetUsd: Union[float, None]
    coverage: Literal["estimated-model-work"]

class PackageLessonsItemFilesItem(TypedDict):
    kind: str
    path: str
    url: str
    contentType: NotRequired[str]
    id: NotRequired[str]

class SourceCoverageMaterialsItemExtracted(TypedDict):
    complete: bool
    characters: int
    sectionIds: list[str]

class SourceCoverageMaterialsItemSelected(TypedDict):
    characters: int
    sections: list["SourceCoverageMaterialsItemSelectedSectionsItem"]

class SourceCoverageMaterialsItemOmitted(TypedDict):
    characters: int
    sectionIds: list[str]

class SourceCoverageMaterialsItemCovered(TypedDict):
    sectionIds: list[str]
    verified: bool

class WebhookEventData0JobFailure(TypedDict):
    code: Literal["materials_unreadable", "content_not_suitable", "generation_failed", "render_failed", "review_rejected", "timed_out", "internal_error"]
    message: str

class QuoteFundedWorkProviderBudgetsSpeech(TypedDict):
    budgetUsd: float
    usdPer1000Characters: float

class SourceCoverageMaterialsItemSelectedSectionsItem(TypedDict):
    id: str
    start: int
    end: int
    complete: bool

