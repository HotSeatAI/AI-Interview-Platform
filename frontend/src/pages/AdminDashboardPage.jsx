import { useEffect, useState } from "react";

import { getAdminUsers, setUserPlan } from "../api/adminApi";
import useAuth from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar.jsx";

const PLANS = ["free", "starter", "pro", "max", "unlimited"];

function AdminDashboardPage() {
  const { token } = useAuth();

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const data = await getAdminUsers(token);
        setUsers(data);
      } catch (err) {
        setError(
          err?.response?.data?.detail || "Failed to load users."
        );
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchUsers();
    }
  }, [token, refreshKey]);

  const handlePlanChange = async (userId, plan) => {
    try {
      setUpdatingId(userId);
      await setUserPlan(userId, plan, token);
      setRefreshKey((prev) => prev + 1);
    } catch (err) {
      setError(
        err?.response?.data?.detail || "Failed to update plan."
      );
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="history-page">
      <Navbar />
      <main className="history-container">
        <div className="section-header">
          <div className="eyebrow">ADMIN</div>
          <h1>User plans</h1>
          <p>Assign or change a user&apos;s plan manually.</p>
        </div>

        {error && <p className="error-text">{error}</p>}

        {loading ? (
          <div className="page-loading">Loading&hellip;</div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="admin-users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Plan</th>
                  <th>Status</th>
                  <th>Interviews</th>
                  <th>Tailorings</th>
                  <th>Change plan</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.username}</td>
                    <td>{user.email}</td>
                    <td>{user.role}</td>
                    <td>{user.plan}</td>
                    <td>{user.status}</td>
                    <td>
                      {user.interviews_used}/{user.interviews_limit}
                    </td>
                    <td>
                      {user.tailorings_used}/{user.tailorings_limit}
                    </td>
                    <td>
                      <select
                        value={user.plan}
                        disabled={updatingId === user.id}
                        onChange={(event) =>
                          handlePlanChange(
                            user.id,
                            event.target.value
                          )
                        }
                      >
                        {PLANS.map((plan) => (
                          <option key={plan} value={plan}>
                            {plan}
                          </option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default AdminDashboardPage;
