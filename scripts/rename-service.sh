#!/bin/bash
# scripts/rename-service.sh
set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/rename-service.sh <new_service_name>"
    echo "Example: ./scripts/rename-service.sh mgraph_ai_service_auth"
    exit 1
fi

OLD_NAME="mgraph_ai_service_llms"
NEW_NAME="$1"
NEW_NAME_HYPHEN=$(echo "$NEW_NAME" | tr '_' '-')

echo "🔄 Renaming service from $OLD_NAME to $NEW_NAME..."

# Rename directories
find . -type d -name "*${OLD_NAME}*" | while read dir; do
    if [[ "$dir" != *".git"* ]]; then
        newdir=$(echo "$dir" | sed "s/$OLD_NAME/$NEW_NAME/g")
        if [ "$dir" != "$newdir" ]; then
            mv "$dir" "$newdir"
            echo "  Renamed directory: $(basename $dir) -> $(basename $newdir)"
        fi
    fi
done

# Replace in all files
find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" -o -name "*.sh" -o -name "*.txt" \) | while read file; do
    # Skip .git directory
    if [[ "$file" == *".git"* ]]; then
        continue
    fi

    # Replace service names
    sed -i.bak "s/$OLD_NAME/$NEW_NAME/g" "$file"

    # Clean up backup files
    rm -f "$file.bak"
done

echo "✅ Service renamed to $NEW_NAME"