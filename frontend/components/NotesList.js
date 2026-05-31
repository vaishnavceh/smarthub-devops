import { useEffect, useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function NotesList({ token }) {
  const [notes, setNotes] = useState([])
  const [newNote, setNewNote] = useState({ title: '', content: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchNotes()
  }, [token])

  const fetchNotes = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/notes?token=${token}`)
      setNotes(response.data)
    } catch (err) {
      console.error('Error fetching notes:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateNote = async (e) => {
    e.preventDefault()
    
    try {
      await axios.post(`${API_URL}/api/notes?token=${token}`, newNote)
      setNewNote({ title: '', content: '' })
      fetchNotes() // Refresh list
    } catch (err) {
      console.error('Error creating note:', err)
    }
  }

  const handleDeleteNote = async (noteId) => {
    try {
      await axios.delete(`${API_URL}/api/notes/${noteId}?token=${token}`)
      fetchNotes() // Refresh list
    } catch (err) {
      console.error('Error deleting note:', err)
    }
  }

  if (loading) return <div>Loading notes...</div>

  return (
    <div className="notes-section">
      <form onSubmit={handleCreateNote} className="note-form">
        <input
          type="text"
          placeholder="Note Title"
          value={newNote.title}
          onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
          required
        />
        <textarea
          placeholder="Note Content"
          value={newNote.content}
          onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
          required
        ></textarea>
        <button type="submit">Add Note</button>
      </form>

      <div className="notes-list">
        {notes.length === 0 ? (
          <p>No notes yet. Create one above!</p>
        ) : (
          notes.map((note) => (
            <div key={note.id} className="note-card">
              <h3>{note.title}</h3>
              <p>{note.content}</p>
              <small>{new Date(note.created_at).toLocaleString()}</small>
              <button 
                onClick={() => handleDeleteNote(note.id)}
                className="delete-btn"
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}