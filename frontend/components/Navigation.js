import { useRouter } from 'next/router'

export default function Navigation({ user }) {
  const router = useRouter()

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/')
  }

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <h1>SmartHub</h1>
      </div>
      <div className="navbar-right">
        <span>{user?.email}</span>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  )
}