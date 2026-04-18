export default function Panel({ title, actions, children }) {
  return (
    <section className="panel">
      <header className="panel-header">
        <div>
          <p className="panel-kicker">{title}</p>
        </div>
        {actions}
      </header>
      <div>{children}</div>
    </section>
  );
}
