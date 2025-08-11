# 🔧 Fix: Unable to See Teacher, Student, and Principal Credentials in Supabase

## 🚨 Problem Identified

The issue is that **Row Level Security (RLS) policies** are blocking the insertion and viewing of users. The RLS policies in the original setup are too restrictive for development.

## ✅ Solution

### Option 1: Quick Fix (Recommended for Development)

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Select your project**: `ywcomtwiavpglsbncftn`
3. **Open SQL Editor**: Click "SQL Editor" in the left sidebar
4. **Create New Query**: Click "New query"
5. **Copy & Paste**: Copy the entire contents of `fix_rls_policies.sql`
6. **Run Script**: Click "Run" to execute

This will:
- ✅ Remove restrictive RLS policies
- ✅ Create permissive policies for development
- ✅ Insert all default users (teachers and principal)
- ✅ Show you the inserted users

### Option 2: Manual Fix via Dashboard

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Navigate to Authentication > Policies**
3. **Find the 'users' table**
4. **Click 'Disable RLS' temporarily**
5. **Go to Table Editor > users**
6. **Manually insert users** or run the SQL script
7. **Re-enable RLS** when done

### Option 3: Run the Fixed Script

After running the SQL fix above, test the connection:

```bash
python3 test_connection.py
```

You should now see users in the database!

## 🔐 Expected Results

After running the fix, you should see these users in your Supabase dashboard:

| Username | Role | Class | Password |
|----------|------|-------|----------|
| principal | principal | NULL | principal123 |
| teacher | teacher | NULL | teacher123 |
| teacher_1 | teacher | 1 | teacher123 |
| teacher_2 | teacher | 2 | teacher123 |
| ... | ... | ... | ... |
| teacher_12 | teacher | 12 | teacher123 |

## 🧪 Test Your Fix

Run this command to verify the fix worked:

```bash
python3 test_connection.py
```

You should see: "📋 Found 15 users in database" instead of 0.

## 🚀 Start Your Application

Once the users are visible, start your application:

```bash
python3 app_supabase.py
```

Then login with:
- **Principal**: `principal` / `principal123`
- **Teachers**: `teacher_1` to `teacher_12` / `teacher123`

## 🔒 Security Note

The fix creates permissive RLS policies for development. For production, you should implement proper role-based access control. The current setup allows all operations for simplicity.

## 🆘 Still Having Issues?

If you still can't see the users:

1. **Check RLS Status**: Go to Authentication > Policies and ensure RLS is properly configured
2. **Verify Table Structure**: Go to Table Editor and check if the 'users' table has the correct columns
3. **Check SQL Errors**: Look for any error messages in the SQL Editor
4. **Contact Support**: The issue might be with your specific Supabase project configuration

---

**Next Step**: Run the `fix_rls_policies.sql` script in your Supabase SQL Editor! 🎯 