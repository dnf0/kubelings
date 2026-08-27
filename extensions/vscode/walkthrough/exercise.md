# Solve Your First Exercise (`pods01`) 🚀

Let's walk through solving the very first challenge: **`pods01.py`** in Chapter 1: Pods.

---

### 📝 Step-by-Step Exercise Walkthrough

1. **Open the Exercise**:
   Click **Open Next Exercise** below or navigate to `exercises/01_pods/pods01.py` in the File Explorer.

2. **Inspect the Broken Manifest**:
   Notice the placeholder values (`???`) in the YAML template:
   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: ???            # Hint: Change to "nginx-web"
     labels:
       app: ???           # Hint: Change to "web"
   spec:
     containers:
     - name: nginx
       image: ???         # Hint: Change to "nginx:alpine"
       ports:
       - containerPort: 0 # Hint: Change to 80
   ```

3. **Fix the Placeholders**:
   Replace `???` with the expected Kubernetes properties.

4. **Verify Your Solution**:
   Save the file or click **Run Current Exercise** below. Once passing, delete `# I AM NOT DONE` to mark the exercise complete!

---

[Open Next Exercise](command:kubelings.nextExercise)
[Run Current Exercise](command:kubelings.runExercise)
