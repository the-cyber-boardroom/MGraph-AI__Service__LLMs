#!/bin/bash
set -e

echo "🚀 Setting up MGraph-AI Service from template..."

# 1. Get repo name and derive service name
REPO_URL=$(git config --get remote.origin.url)
REPO_NAME=$(basename -s .git "$REPO_URL")

# Extract service name (MGraph-AI__Service__Auth -> mgraph_ai_service_auth)
SERVICE_NAME=$(echo "$REPO_NAME" | sed 's/MGraph-AI__Service__/mgraph_ai_service_/' | tr '[:upper:]' '[:lower:]' | tr '-' '_')
SERVICE_DISPLAY_NAME=$(echo "$REPO_NAME" | sed 's/__/ /g' | sed 's/-/ /g')

echo "📦 Repository: $REPO_NAME"
echo "🔧 Service name: $SERVICE_NAME"
echo "📋 Display name: $SERVICE_DISPLAY_NAME"

# 2. Add template remote and pull
echo "📥 Pulling from template..."
git remote add template https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs.git || true
git fetch template
git merge template/main --allow-unrelated-histories -m "Initial template import" || {
    echo "⚠️  Merge conflict detected. This is normal for the first setup."
    echo "Attempting to resolve automatically..."
}

# 3. Rename template service to actual service
echo "🔄 Renaming service..."

# Rename directories
find . -type d -name "*mgraph_ai_service_llms*" | while read dir; do
    if [[ "$dir" != *".git"* ]]; then
        newdir=$(echo "$dir" | sed "s/mgraph_ai_service_llms/$SERVICE_NAME/g")
        if [ "$dir" != "$newdir" ]; then
            mv "$dir" "$newdir"
            echo "  Renamed: $dir -> $newdir"
        fi
    fi
done

# Replace in all files
find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" -o -name "*.sh" -o -name "*.txt" \) | while read file; do
    # Skip .git directory and this script
    if [[ "$file" == *".git"* ]] || [[ "$file" == *"setup-from-template.sh"* ]]; then
        continue
    fi

    # Create backup
    cp "$file" "$file.bak"

    # Replace service names
    sed -i.tmp "s/mgraph_ai_service_llms/$SERVICE_NAME/g" "$file"
    sed -i.tmp "s/MGraph-AI__Service__LLMs/$REPO_NAME/g" "$file"
    sed -i.tmp "s/MGraph-AI Service LLMs/$SERVICE_DISPLAY_NAME/g" "$file"

    # Clean up temp files
    rm -f "$file.tmp"

    # Check if file was modified
    if ! cmp -s "$file" "$file.bak"; then
        echo "  Updated: $file"
    fi
    rm -f "$file.bak"
done

# 4. Update version to v0.1.0
echo "v0.1.0" > "$SERVICE_NAME/version"

# 5. Create .template directory for tracking
mkdir -p .template
cat > .template/VERSION << EOF
TEMPLATE_VERSION=1.0.0
TEMPLATE_COMMIT=$(git rev-parse template/main 2>/dev/null || echo "unknown")
CREATED_DATE=$(date -u +%Y-%m-%d)
SERVICE_NAME=$SERVICE_NAME
REPO_NAME=$REPO_NAME
EOF

# 6. Clean up any merge artifacts
find . -name "*.orig" -delete

# 7. Stage all changes
echo "💾 Staging changes..."
git add -A

# 8. Check if we need to resolve conflicts
if git status --porcelain | grep -q "^UU"; then
    echo "⚠️  Merge conflicts need to be resolved manually"
    echo "After resolving conflicts, run:"
    echo "  git add ."
    echo "  git commit -m 'Initialize $SERVICE_DISPLAY_NAME from template'"
    echo "  git push -u origin main"
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Initialize $SERVICE_DISPLAY_NAME from template

- Based on MGraph-AI__Service__LLMs v1.0.0
- Service name: $SERVICE_NAME
- Repository: $REPO_NAME" || echo "No changes to commit"

    # 9. Push to origin
    echo "⬆️  Pushing to GitHub..."
    git push -u origin main || echo "⚠️  Could not push. You may need to run: git push -u origin main"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Review the generated files"
echo "2. Update the README.md with your service details"
echo "3. Configure GitHub secrets for deployment"
echo "4. Run: pip install -r requirements-test.txt"
echo "5. Run: ./scripts/run-locally.sh"
echo ""
echo "🔄 To pull future template updates:"
echo "   git fetch template"
echo "   git merge template/main"