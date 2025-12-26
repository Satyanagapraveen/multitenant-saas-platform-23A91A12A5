import { useForm } from "react-hook-form";
import api from "../../api/axios";

function CreateProjectModal({ onClose, onSuccess }) {
  const { register, handleSubmit } = useForm();

  const onSubmit = async (data) => {
    await api.post("/projects", data);
    onSuccess();
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="bg-white p-6 rounded w-96 space-y-3"
      >
        <h3 className="font-bold text-lg">Create Project</h3>

        <input
          {...register("name", { required: true })}
          placeholder="Project name"
          className="input"
        />

        <textarea
          {...register("description")}
          placeholder="Description"
          className="input"
        />

        <select {...register("status")} className="input">
          <option value="active">Active</option>
          <option value="archived">Archived</option>
          <option value="completed">Completed</option>
        </select>

        <div className="flex justify-end gap-2">
          <button type="button" onClick={onClose}>
            Cancel
          </button>
          <button className="bg-blue-600 text-white px-3 py-1 rounded">
            Save
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreateProjectModal;
