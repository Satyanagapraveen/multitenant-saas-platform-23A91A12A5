function StatsCards({ stats }) {
  if (!stats) return null;

  const cards = [
    { label: "Total Projects", value: stats.totalProjects },
    { label: "Total Tasks", value: stats.totalTasks },
    { label: "Completed Tasks", value: stats.completedTasks },
    { label: "Pending Tasks", value: stats.pendingTasks },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <div
          key={index}
          className="bg-white shadow rounded p-4 text-center"
        >
          <p className="text-gray-500">{card.label}</p>
          <p className="text-2xl font-bold">{card.value}</p>
        </div>
      ))}
    </div>
  );
}

export default StatsCards;
