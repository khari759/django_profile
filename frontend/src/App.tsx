import { About } from "./components/About";
import { Contact } from "./components/Contact";
import { Credentials } from "./components/Credentials";
import { ExperienceTimeline } from "./components/ExperienceTimeline";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { Projects } from "./components/Projects";
import { Skills } from "./components/Skills";
import { EmptyProfileScreen, ErrorScreen, LoadingScreen } from "./components/StatusScreens";
import { useOverview } from "./hooks/useOverview";
import { useTheme } from "./hooks/useTheme";

/** Skills shown in the About sidebar: the first few from each category. */
const CORE_SKILL_LIMIT = 8;

export default function App() {
  const { state, retry } = useOverview();
  const { theme, toggleTheme } = useTheme();

  if (state.status === "loading") return <LoadingScreen />;
  if (state.status === "error") {
    return <ErrorScreen message={state.message} onRetry={retry} />;
  }

  const { profile, skill_categories, experience, projects, education, certifications } =
    state.data;

  if (!profile) return <EmptyProfileScreen />;

  const allSkills = skill_categories.flatMap((category) => category.skills);
  const topSkills = skill_categories
    .flatMap((category) => category.skills.slice(0, 2))
    .slice(0, CORE_SKILL_LIMIT)
    .map((skill) => skill.name);

  return (
    <>
      <a className="skip-link" href="#about">
        Skip to content
      </a>
      <Header name={profile.full_name} theme={theme} onToggleTheme={toggleTheme} />
      <main>
        <Hero
          profile={profile}
          projectCount={projects.length}
          skillCount={allSkills.length}
        />
        <About profile={profile} topSkills={topSkills} />
        <Skills categories={skill_categories} />
        <ExperienceTimeline roles={experience} />
        <Projects projects={projects} />
        <Credentials education={education} certifications={certifications} />
        <Contact profile={profile} />
      </main>
      <Footer name={profile.full_name} githubUrl={profile.github_url} />
    </>
  );
}
