"""Localization Wizard

Internationalization (i18n) and localization (L10n), translations, multi-language support.
Uses Empathy Framework Level 3 (Proactive) for string extraction and Level 4
(Anticipatory) for predicting localization challenges and cultural issues.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from typing import Any

from .base_wizard import (
    BaseWizard,
    EmpathyChecks,
    WizardArtifact,
    WizardHandoff,
    WizardOutput,
    WizardRisk,
    WizardTask,
)


class LocalizationWizard(BaseWizard):
    """Wizard for internationalization and localization

    Uses:
    - Level 2: Guide user through i18n setup
    - Level 3: Proactively extract translatable strings
    - Level 4: Anticipate localization challenges (RTL, plurals, cultural)
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a localization task"""
        # High-priority localization phrases (worth 2 points each)
        localization_phrases = [
            "i18n",
            "l10n",
            "localization",
            "translation",
            "internationalization",
        ]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "locale",
            "language",
            "multilingual",
            "translate",
            "rtl",
            "right-to-left",
            "arabic",
            "japanese",
            "chinese",
            "spanish",
            "gettext",
            "format.js",
            "react-intl",
            "django-i18n",
        ]

        task_lower = (task.task + " " + task.context).lower()

        primary_matches = sum(2 for phrase in localization_phrases if phrase in task_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute localization workflow"""
        self._assess_emotional_state(task)
        self._extract_constraints(task)

        diagnosis = self._analyze_localization_requirements(task)
        string_extraction = self._extract_strings(task)
        framework_setup = self._recommend_i18n_framework(task)
        translation_files = self._generate_translation_files(task, string_extraction)
        rtl_support = self._implement_rtl_support(task)
        localization_forecast = self._predict_localization_challenges(task, string_extraction)

        artifacts = [
            WizardArtifact(
                type="doc",
                title="Localization Strategy",
                content=self._generate_localization_strategy(diagnosis, framework_setup),
            ),
            WizardArtifact(type="code", title="i18n Framework Setup", content=framework_setup),
            WizardArtifact(
                type="code",
                title="Translation Files (JSON)",
                content=translation_files,
            ),
            WizardArtifact(type="code", title="RTL (Right-to-Left) Support", content=rtl_support),
            WizardArtifact(
                type="doc",
                title="Translation Workflow Guide",
                content=self._create_translation_workflow(task),
            ),
            WizardArtifact(
                type="doc",
                title="Localization Forecast",
                content=localization_forecast,
            ),
        ]

        plan = [
            "1. Set up i18n framework (react-intl, django-i18n, etc.)",
            "2. Extract all hardcoded strings",
            "3. Create translation files for target languages",
            "4. Implement locale switching UI",
            "5. Add RTL support for Arabic/Hebrew",
            "6. Handle date/time/currency formatting",
            "7. Test with all target locales",
        ]

        empathy_checks = EmpathyChecks(
            cognitive="Considered global users: language barriers, cultural differences, reading direction",
            emotional="Acknowledged: Users feel excluded when app not in their language",
            anticipatory=(
                localization_forecast[:200] + "..."
                if len(localization_forecast) > 200
                else localization_forecast
            ),
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=plan,
            artifacts=artifacts,
            risks=self._identify_risks(task, plan),
            handoffs=self._create_handoffs(task),
            next_actions=plan[:3] + self._generate_anticipatory_actions(task),
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task),
        )

    def _analyze_localization_requirements(self, task: WizardTask) -> str:
        """Analyze localization requirements"""
        analysis = "# Localization Requirements Analysis\n\n"
        analysis += f"**Objective**: {task.task}\n\n"

        task_lower = (task.task + " " + task.context).lower()

        # Detect target languages
        languages = []
        if any(kw in task_lower for kw in ["spanish", "español"]):
            languages.append("Spanish (es)")
        if any(kw in task_lower for kw in ["french", "français"]):
            languages.append("French (fr)")
        if any(kw in task_lower for kw in ["german", "deutsch"]):
            languages.append("German (de)")
        if any(kw in task_lower for kw in ["chinese", "中文"]):
            languages.append("Chinese (zh)")
        if any(kw in task_lower for kw in ["japanese", "日本語"]):
            languages.append("Japanese (ja)")
        if any(kw in task_lower for kw in ["arabic", "العربية", "rtl"]):
            languages.append("Arabic (ar) - RTL")
        if any(kw in task_lower for kw in ["hebrew", "עברית"]):
            languages.append("Hebrew (he) - RTL")

        if not languages:
            languages = ["Spanish (es)", "French (fr)", "German (de)"]

        analysis += f"**Target Languages**: {', '.join(languages)}\n"
        analysis += f"**RTL Support Needed**: {'Yes' if 'RTL' in ', '.join(languages) else 'No'}\n"
        analysis += (
            f"**Context**: {task.context[:300]}...\n"
            if len(task.context) > 300
            else f"**Context**: {task.context}\n"
        )

        return analysis

    def _extract_strings(self, task: WizardTask) -> list[dict[str, Any]]:
        """Extract translatable strings (Level 3: Proactive)"""
        strings = [
            {
                "key": "welcome.title",
                "text": "Welcome to our application",
                "context": "Homepage hero section",
                "notes": "Keep friendly and welcoming tone",
            },
            {
                "key": "auth.login",
                "text": "Log in",
                "context": "Login button",
                "notes": "Action verb, keep concise",
            },
            {
                "key": "auth.login.error",
                "text": "Invalid email or password",
                "context": "Login error message",
                "notes": "Don't reveal which field is wrong (security)",
            },
            {
                "key": "items.count",
                "text": "{count, plural, =0 {No items} =1 {1 item} other {# items}}",
                "context": "Item counter",
                "notes": "Plural forms vary by language",
            },
            {
                "key": "date.format",
                "text": "{date, date, long}",
                "context": "Date formatting",
                "notes": "Locale-specific format",
            },
        ]

        return strings

    def _recommend_i18n_framework(self, task: WizardTask) -> str:
        """Recommend and set up i18n framework"""
        framework = "# Internationalization Framework Setup\n\n"

        task_lower = (task.task + " " + task.context).lower()

        # React/Frontend
        if any(kw in task_lower for kw in ["react", "frontend", "javascript"]):
            framework += "## React: react-intl (Format.js)\n\n"
            framework += "### Installation\n"
            framework += "```bash\n"
            framework += "npm install react-intl\n"
            framework += "```\n\n"

            framework += "### Setup\n"
            framework += "```javascript\n"
            framework += "// src/i18n/i18n.js\n"
            framework += (
                "import { createIntl, createIntlCache, RawIntlProvider } from 'react-intl';\n\n"
            )
            framework += "const cache = createIntlCache();\n\n"
            framework += "const messages = {\n"
            framework += "  en: () => import('./locales/en.json'),\n"
            framework += "  es: () => import('./locales/es.json'),\n"
            framework += "  fr: () => import('./locales/fr.json'),\n"
            framework += "};\n\n"

            framework += "export async function getIntl(locale = 'en') {\n"
            framework += "  const messages = await messages[locale]();\n"
            framework += "  return createIntl({ locale, messages }, cache);\n"
            framework += "}\n\n"

            framework += "// App.jsx\n"
            framework += "import { IntlProvider } from 'react-intl';\n"
            framework += "import { useState } from 'react';\n\n"
            framework += "function App() {\n"
            framework += "  const [locale, setLocale] = useState('en');\n"
            framework += "  const [messages, setMessages] = useState({});\n\n"
            framework += "  useEffect(() => {\n"
            framework += "    import(`./locales/${locale}.json`).then(msgs => setMessages(msgs));\n"
            framework += "  }, [locale]);\n\n"
            framework += "  return (\n"
            framework += "    <IntlProvider locale={locale} messages={messages}>\n"
            framework += "      <YourApp />\n"
            framework += "    </IntlProvider>\n"
            framework += "  );\n"
            framework += "}\n"
            framework += "```\n\n"

            framework += "### Usage in Components\n"
            framework += "```javascript\n"
            framework += "import { FormattedMessage, useIntl } from 'react-intl';\n\n"
            framework += "function Welcome() {\n"
            framework += "  const intl = useIntl();\n\n"
            framework += "  return (\n"
            framework += "    <div>\n"
            framework += "      {/* Declarative */}\n"
            framework += '      <h1><FormattedMessage id="welcome.title" /></h1>\n\n'
            framework += "      {/* Imperative */}\n"
            framework += "      <button title={intl.formatMessage({ id: 'auth.login' })}>\n"
            framework += "        {intl.formatMessage({ id: 'auth.login' })}\n"
            framework += "      </button>\n\n"
            framework += "      {/* Plurals */}\n"
            framework += "      <FormattedMessage \n"
            framework += '        id="items.count" \n'
            framework += "        values={{ count: items.length }} \n"
            framework += "      />\n\n"
            framework += "      {/* Dates */}\n"
            framework += '      <FormattedDate value={new Date()} year="numeric" month="long" day="numeric" />\n'
            framework += "    </div>\n"
            framework += "  );\n"
            framework += "}\n"
            framework += "```\n\n"

        # Python/Django
        if any(kw in task_lower for kw in ["python", "django", "backend"]):
            framework += "## Django: Built-in i18n\n\n"
            framework += "### Settings\n"
            framework += "```python\n"
            framework += "# settings.py\n"
            framework += "LANGUAGE_CODE = 'en-us'\n"
            framework += "USE_I18N = True\n"
            framework += "USE_L10N = True\n\n"
            framework += "LANGUAGES = [\n"
            framework += "    ('en', 'English'),\n"
            framework += "    ('es', 'Spanish'),\n"
            framework += "    ('fr', 'French'),\n"
            framework += "]\n\n"
            framework += "LOCALE_PATHS = [BASE_DIR / 'locale']\n"
            framework += "```\n\n"

            framework += "### Usage in Code\n"
            framework += "```python\n"
            framework += "from django.utils.translation import gettext as _, ngettext\n\n"
            framework += "# Simple translation\n"
            framework += 'message = _("Welcome to our application")\n\n'
            framework += "# Pluralization\n"
            framework += "count = 5\n"
            framework += "message = ngettext(\n"
            framework += "    '%(count)d item',\n"
            framework += "    '%(count)d items',\n"
            framework += "    count\n"
            framework += ") % {'count': count}\n"
            framework += "```\n\n"

            framework += "### Extract and Compile\n"
            framework += "```bash\n"
            framework += "# Extract strings to .po files\n"
            framework += "python manage.py makemessages -l es\n"
            framework += "python manage.py makemessages -l fr\n\n"
            framework += "# Translate in locale/es/LC_MESSAGES/django.po\n\n"
            framework += "# Compile to .mo files\n"
            framework += "python manage.py compilemessages\n"
            framework += "```\n\n"

        return framework

    def _generate_translation_files(self, task: WizardTask, strings: list[dict]) -> str:
        """Generate translation files"""
        files = "# Translation Files\n\n"

        files += "## English (en.json)\n\n"
        files += "```json\n"
        files += "{\n"
        for i, s in enumerate(strings):
            comma = "," if i < len(strings) - 1 else ""
            files += f'  "{s["key"]}": "{s["text"]}"{comma}\n'
        files += "}\n"
        files += "```\n\n"

        files += "## Spanish (es.json)\n\n"
        files += "```json\n"
        files += "{\n"
        translations = {
            "welcome.title": "Bienvenido a nuestra aplicación",
            "auth.login": "Iniciar sesión",
            "auth.login.error": "Correo electrónico o contraseña inválidos",
            "items.count": "{count, plural, =0 {Sin artículos} =1 {1 artículo} other {# artículos}}",
            "date.format": "{date, date, long}",
        }
        for i, s in enumerate(strings):
            key = s["key"]
            # Use translated text if available, otherwise use fallback with English text
            # In production: integrate with translation service API or use machine translation
            if key in translations:
                text = translations[key]
            else:
                # Fallback: Use English text with note for translators
                text = f"{s['text']} [ES: Pending translation]"
            comma = "," if i < len(strings) - 1 else ""
            files += f'  "{key}": "{text}"{comma}\n'
        files += "}\n"
        files += "```\n\n"

        files += "## Translation Notes\n\n"
        files += "| Key | Context | Notes |\n"
        files += "|-----|---------|-------|\n"
        for s in strings:
            files += f"| `{s['key']}` | {s['context']} | {s['notes']} |\n"

        return files

    def _implement_rtl_support(self, task: WizardTask) -> str:
        """Implement RTL support"""
        rtl = "# RTL (Right-to-Left) Support\n\n"

        rtl += "## CSS for RTL Languages (Arabic, Hebrew)\n\n"
        rtl += "```css\n"
        rtl += "/* Automatically flip layout for RTL */\n"
        rtl += 'html[dir="rtl"] {\n'
        rtl += "  direction: rtl;\n"
        rtl += "}\n\n"

        rtl += "/* Use logical properties (automatically flips) */\n"
        rtl += ".container {\n"
        rtl += "  padding-inline-start: 20px;  /* Left in LTR, right in RTL */\n"
        rtl += "  padding-inline-end: 10px;    /* Right in LTR, left in RTL */\n"
        rtl += "  margin-inline: auto;         /* Horizontal margins */\n"
        rtl += "}\n\n"

        rtl += "/* Avoid these (not RTL-friendly): */\n"
        rtl += ".bad-example {\n"
        rtl += "  padding-left: 20px;   /* Won't flip! */\n"
        rtl += "  float: left;          /* Won't flip! */\n"
        rtl += "}\n\n"

        rtl += "/* Better: */\n"
        rtl += ".good-example {\n"
        rtl += "  padding-inline-start: 20px;  /* Flips automatically */\n"
        rtl += "  float: inline-start;         /* Flips automatically */\n"
        rtl += "}\n"
        rtl += "```\n\n"

        rtl += "## JavaScript: Detect and Set Direction\n\n"
        rtl += "```javascript\n"
        rtl += "// Detect RTL languages\n"
        rtl += "const RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur'];\n\n"
        rtl += "function setDirection(locale) {\n"
        rtl += "  const isRTL = RTL_LANGUAGES.includes(locale);\n"
        rtl += "  document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');\n"
        rtl += "  document.documentElement.setAttribute('lang', locale);\n"
        rtl += "}\n\n"
        rtl += "// Call when locale changes\n"
        rtl += "setDirection('ar');  // Arabic: RTL\n"
        rtl += "setDirection('en');  // English: LTR\n"
        rtl += "```\n\n"

        rtl += "## React: RTL with Styled Components\n\n"
        rtl += "```javascript\n"
        rtl += "import { createGlobalStyle } from 'styled-components';\n\n"
        rtl += "const GlobalStyle = createGlobalStyle`\n"
        rtl += '  html[dir="rtl"] {\n'
        rtl += "    direction: rtl;\n"
        rtl += "  }\n"
        rtl += "  \n"
        rtl += '  html[dir="ltr"] {\n'
        rtl += "    direction: ltr;\n"
        rtl += "  }\n"
        rtl += "`;\n\n"
        rtl += "function App({ locale }) {\n"
        rtl += "  const isRTL = ['ar', 'he'].includes(locale);\n"
        rtl += "  \n"
        rtl += "  return (\n"
        rtl += "    <div dir={isRTL ? 'rtl' : 'ltr'}>\n"
        rtl += "      <GlobalStyle />\n"
        rtl += "      <YourApp />\n"
        rtl += "    </div>\n"
        rtl += "  );\n"
        rtl += "}\n"
        rtl += "```\n\n"

        rtl += "## Common RTL Gotchas\n\n"
        rtl += "1. **Icons**: Some icons need mirroring (arrows), others don't (play button)\n"
        rtl += "2. **Numbers**: Numbers stay LTR even in RTL text\n"
        rtl += "3. **Scrollbars**: Position flips in RTL\n"
        rtl += "4. **Animations**: May need to reverse direction\n"

        return rtl

    def _create_translation_workflow(self, task: WizardTask) -> str:
        """Create translation workflow guide"""
        workflow = "# Translation Workflow\n\n"

        workflow += "## Step 1: String Extraction\n\n"
        workflow += "Extract all user-facing strings from code:\n\n"
        workflow += "```bash\n"
        workflow += "# React (formatjs CLI)\n"
        workflow += "npx formatjs extract 'src/**/*.{js,jsx,ts,tsx}' --out-file lang/en.json\n\n"
        workflow += "# Django\n"
        workflow += "python manage.py makemessages -l es\n"
        workflow += "```\n\n"

        workflow += "## Step 2: Translation\n\n"
        workflow += "### Option A: Professional Translation Service\n"
        workflow += "- **Recommended for**: Product launch, marketing content\n"
        workflow += "- **Services**: Smartling, Lokalise, Phrase\n"
        workflow += "- **Cost**: $0.10-0.20 per word\n"
        workflow += "- **Quality**: Native speakers, cultural adaptation\n\n"

        workflow += "### Option B: Machine Translation (Initial)\n"
        workflow += "- **Use for**: Development/testing, first draft\n"
        workflow += "- **Services**: Google Translate API, DeepL API\n"
        workflow += "- **Cost**: ~$20 per 1M characters\n"
        workflow += "- **Quality**: Good for basic text, needs human review\n\n"

        workflow += "### Option C: Crowdsourced\n"
        workflow += "- **Use for**: Community-driven projects\n"
        workflow += "- **Platforms**: Crowdin, Transifex\n"
        workflow += "- **Cost**: Free (community volunteers)\n"
        workflow += "- **Quality**: Varies, needs moderation\n\n"

        workflow += "## Step 3: Quality Assurance\n\n"
        workflow += "- [ ] Native speaker review\n"
        workflow += "- [ ] Test in-app (length, formatting)\n"
        workflow += "- [ ] Check pluralization rules\n"
        workflow += "- [ ] Verify cultural appropriateness\n"
        workflow += "- [ ] Test RTL languages (Arabic, Hebrew)\n\n"

        workflow += "## Step 4: Continuous Updates\n\n"
        workflow += "```yaml\n"
        workflow += "# GitHub Actions: Auto-sync translations\n"
        workflow += "name: Sync Translations\n"
        workflow += "on:\n"
        workflow += "  push:\n"
        workflow += "    paths:\n"
        workflow += "      - 'src/**/*.{js,jsx}'\n"
        workflow += "jobs:\n"
        workflow += "  sync:\n"
        workflow += "    runs-on: ubuntu-latest\n"
        workflow += "    steps:\n"
        workflow += "      - name: Extract strings\n"
        workflow += "        run: npx formatjs extract\n"
        workflow += "      - name: Upload to translation service\n"
        workflow += "        run: lokalise --push\n"
        workflow += "```\n\n"

        workflow += "## Translation Memory\n\n"
        workflow += "Maintain a glossary for consistency:\n\n"
        workflow += "| English | Spanish | French | Notes |\n"
        workflow += "|---------|---------|--------|---------|\n"
        workflow += "| Log in | Iniciar sesión | Se connecter | Action (verb) |\n"
        workflow += "| Account | Cuenta | Compte | Noun |\n"
        workflow += "| Settings | Configuración | Paramètres | Noun |\n"

        return workflow

    def _predict_localization_challenges(self, task: WizardTask, strings: list[dict]) -> str:
        """Level 4: Predict localization challenges"""
        forecast = "# Localization Forecast (Level 4: Anticipatory)\n\n"

        forecast += "## Current State\n"
        forecast += f"- Strings to translate: {len(strings)}\n"
        forecast += "- Target languages: 3-5 initially\n"
        forecast += "- RTL support: Needs implementation\n\n"

        forecast += "## Projected Challenges (Next 30-90 Days)\n\n"

        forecast += "### ⚠️ Text Expansion Breaks UI (Week 2)\n"
        forecast += (
            "**Prediction**: German text 30% longer than English, breaks fixed-width layouts\n"
        )
        forecast += "**Impact**: Broken UI, text overflow, poor UX in German locale\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Use flexible layouts (min-width, not fixed width)\n"
        forecast += "- Test with pseudo-localization (XXXXXXX)\n"
        forecast += "- Reserve 30-50% extra space for text expansion\n"
        forecast += "- Truncate gracefully with ellipsis if needed\n\n"

        forecast += "### ⚠️ Pluralization Bugs (Week 3)\n"
        forecast += "**Prediction**: Naive pluralization (count !== 1 ? 's' : '') fails in Slavic languages\n"
        forecast += '**Impact**: "1 items", "21 item" - grammatically incorrect\n'
        forecast += "**Cause**: Russian/Polish have 3-4 plural forms, not just 2\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Use ICU MessageFormat for plurals\n"
        forecast += '- Never concatenate strings ("Count: " + count + " items")\n'
        forecast += "- Test with languages having complex plurals (Polish, Arabic)\n\n"

        forecast += "### ⚠️ Date/Time Confusion (Week 4)\n"
        forecast += "**Prediction**: American date format (MM/DD/YYYY) confuses European users\n"
        forecast += "**Impact**: 01/06/2025 = Jan 6 or June 1?\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Use locale-aware formatting (Intl.DateTimeFormat)\n"
        forecast += '- Show full month name to avoid confusion ("January 6, 2025")\n'
        forecast += "- Use ISO 8601 for data storage (YYYY-MM-DD)\n\n"

        forecast += "### ⚠️ RTL Layout Chaos (30 days)\n"
        forecast += (
            "**Prediction**: Arabic/Hebrew users see broken layouts (text flows wrong direction)\n"
        )
        forecast += "**Impact**: Unusable interface for 5% of global users\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Use CSS logical properties (padding-inline-start, not padding-left)\n"
        forecast += "- Test with Arabic from day 1\n"
        forecast += "- Avoid embedding directional icons in strings\n\n"

        forecast += "### ⚠️ Cultural Insensitivity (45 days)\n"
        forecast += "**Prediction**: Idioms, humor, cultural references don't translate\n"
        forecast += "**Impact**: Confusion, offense, brand damage\n"
        forecast += "**Examples**:\n"
        forecast += '- "Piece of cake" → Meaningless in other languages\n'
        forecast += "- Red = danger (China: red = prosperity)\n"
        forecast += "- Thumbs up 👍 (offensive in some Middle Eastern countries)\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Avoid idioms in UI text\n"
        forecast += "- Cultural review by native speakers\n"
        forecast += "- Use culturally neutral icons and colors\n\n"

        forecast += "### ⚠️ Translation Debt Accumulation (60 days)\n"
        forecast += "**Prediction**: Without automation, translations lag behind code changes\n"
        forecast += "**Impact**: Half-translated UI, poor UX, users switch back to English\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Integrate translation service with CI/CD\n"
        forecast += "- Block merges if untranslated strings detected\n"
        forecast += "- Set up translation memory to reuse existing translations\n\n"

        forecast += "## Recommended Timeline\n"
        forecast += "- **Week 1**: Set up i18n framework, extract strings\n"
        forecast += "- **Week 2**: Translate to 1-2 priority languages\n"
        forecast += "- **Week 3**: Implement RTL support\n"
        forecast += "- **Week 4**: Test with native speakers\n"
        forecast += "- **Ongoing**: Continuous translation sync\n"

        return forecast

    def _generate_localization_strategy(self, diagnosis: str, framework_setup: str) -> str:
        """Generate localization strategy document"""
        strategy = f"{diagnosis}\n\n"

        strategy += "## Localization Strategy\n\n"

        strategy += "### Phase 1: Foundation (Weeks 1-2)\n"
        strategy += "- Set up i18n framework\n"
        strategy += "- Extract all user-facing strings\n"
        strategy += "- Create English base locale file\n"
        strategy += "- Implement locale switching UI\n\n"

        strategy += "### Phase 2: Initial Locales (Weeks 3-4)\n"
        strategy += "- Translate to top 2-3 priority languages\n"
        strategy += "- Professional translation for critical content\n"
        strategy += "- Machine translation for less critical content\n"
        strategy += "- Native speaker QA\n\n"

        strategy += "### Phase 3: RTL Support (Week 5)\n"
        strategy += "- Implement RTL layout support\n"
        strategy += "- Test with Arabic/Hebrew\n"
        strategy += "- Fix layout issues\n\n"

        strategy += "### Phase 4: Continuous Localization (Ongoing)\n"
        strategy += "- Automated string extraction in CI/CD\n"
        strategy += "- Continuous sync with translation service\n"
        strategy += "- Monitor translation coverage\n"

        return strategy

    def _identify_risks(self, task: WizardTask, plan: list[str]) -> list[WizardRisk]:
        """Identify localization risks"""
        risks = []

        risks.append(
            WizardRisk(
                risk="Translation quality issues lead to poor UX or brand damage",
                mitigation="Use professional translators for critical content. Native speaker review before launch.",
                severity="high",
            ),
        )

        risks.append(
            WizardRisk(
                risk="Hardcoded strings missed during extraction, breaking localized UI",
                mitigation="Automated string extraction in CI/CD. Fail builds if hardcoded strings detected.",
                severity="medium",
            ),
        )

        risks.append(
            WizardRisk(
                risk="RTL layout breaks UI for Arabic/Hebrew users",
                mitigation="Use CSS logical properties. Test with RTL languages from day 1.",
                severity="high",
            ),
        )

        risks.append(
            WizardRisk(
                risk="Translation debt accumulates faster than team can handle",
                mitigation="Integrate with translation service (Lokalise, Phrase). Automate translation workflow.",
                severity="medium",
            ),
        )

        return risks

    def _create_handoffs(self, task: WizardTask) -> list[WizardHandoff]:
        """Create handoffs for localization work"""
        handoffs = []

        if task.role == "developer":
            handoffs.append(
                WizardHandoff(
                    owner="Translation Team / Service",
                    what="Translate extracted strings, maintain translation memory, cultural adaptation",
                    when="Continuously as strings are added",
                ),
            )
            handoffs.append(
                WizardHandoff(
                    owner="Native Speaker Reviewers",
                    what="QA translations, test in-app, verify cultural appropriateness",
                    when="Before each release",
                ),
            )

        return handoffs
