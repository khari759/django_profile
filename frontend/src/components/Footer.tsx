interface FooterProps {
  name: string;
  githubUrl: string;
}

export function Footer({ name, githubUrl }: FooterProps) {
  return (
    <footer className="footer">
      <p>
        © {new Date().getFullYear()} {name}. Built with Django REST Framework and React.
      </p>
      {githubUrl ? (
        <a href={githubUrl} target="_blank" rel="noreferrer">
          Source on GitHub
        </a>
      ) : null}
    </footer>
  );
}
