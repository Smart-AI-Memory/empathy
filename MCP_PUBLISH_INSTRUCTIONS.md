# MCP Registry Publish Instructions for MemDocs

## Status: Ready to Publish (after PyPI update)

### What's Already Done
- [x] Built MCP Registry publisher CLI at `/tmp/mcp-registry/bin/mcp-publisher`
- [x] GitHub authentication completed (as `silversurfer562`)
- [x] Added `mcp-name: io.github.silversurfer562/memdocs` to MemDocs README.md
- [x] Bumped version to 2.0.17 in `pyproject.toml`
- [x] Created `server.json` configuration

### What You Need to Do in MemDocs Project

#### Step 1: Verify Changes
```bash
cd /Users/patrickroebuck/projects/memdocs

# Verify mcp-name was added to README
grep "mcp-name" README.md
# Should show: <!-- mcp-name: io.github.silversurfer562/memdocs -->

# Verify version bump
grep "^version" pyproject.toml
# Should show: version = "2.0.17"
```

#### Step 2: Commit and Push Changes
```bash
git add README.md pyproject.toml
git commit -m "Add MCP Registry metadata and bump to 2.0.17"
git push origin main
```

#### Step 3: Build and Publish to PyPI
```bash
# Clean and build
rm -rf dist/
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

#### Step 4: Wait for PyPI to Update
PyPI typically takes 1-5 minutes to index the new version. Verify at:
https://pypi.org/project/memdocs/2.0.17/

---

### What You Need to Do in Empathy Framework Project

#### Step 5: Re-authenticate (token may have expired)
```bash
/tmp/mcp-registry/bin/mcp-publisher login github
```
- Go to: https://github.com/login/device
- Enter the code shown
- Authorize the application

#### Step 6: Publish to MCP Registry
```bash
cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework
/tmp/mcp-registry/bin/mcp-publisher publish
```

Expected success output:
```
Publishing to https://registry.modelcontextprotocol.io...
✓ Successfully published io.github.silversurfer562/memdocs@2.0.17
```

---

### Troubleshooting

#### If publisher CLI doesn't exist
```bash
cd /tmp
git clone https://github.com/modelcontextprotocol/registry.git mcp-registry
cd mcp-registry
make publisher
```

#### If token expired
```bash
/tmp/mcp-registry/bin/mcp-publisher login github
```

#### If namespace error
The server must be published under `io.github.silversurfer562/*` since that's the authenticated GitHub account.

#### If README validation fails
Ensure the MemDocs README on PyPI contains:
```
mcp-name: io.github.silversurfer562/memdocs
```
(Can be in an HTML comment)

---

### Registry Verification
After successful publish, verify at:
- https://registry.modelcontextprotocol.io/servers/io.github.silversurfer562/memdocs

---

## Summary Checklist

- [ ] MemDocs: Verify README has mcp-name comment
- [ ] MemDocs: Verify version is 2.0.17
- [ ] MemDocs: Commit and push changes
- [ ] MemDocs: Build package (`python -m build`)
- [ ] MemDocs: Upload to PyPI (`twine upload dist/*`)
- [ ] PyPI: Wait for indexing (check pypi.org)
- [ ] Empathy: Re-authenticate if needed (`mcp-publisher login github`)
- [ ] Empathy: Publish to registry (`mcp-publisher publish`)
- [ ] Registry: Verify listing exists

---

*Generated: 2025-11-30*
