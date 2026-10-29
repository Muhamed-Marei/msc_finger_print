'use client';

import React, { useState, useEffect } from 'react';
import {
  FileSpreadsheet,
  FileText,
  Upload,
  Search,
  Clock,
  AlertTriangle,
  Award,
  Users,
  RefreshCw,
  Sun,
  Moon,
  Eye,
  Download,
  X,
  CheckCircle2,
  Calendar,
  Layers,
  History,
  Trash2,
  ChevronDown,
  FolderArchive,
  FileCheck,
  PlusCircle,
  Edit3,
  Save,
  Plus,
  FilePlus2,
  CalendarClock,
  Sparkles,
  AlertCircle,
  FilterX,
  Check,
  Filter,
  UserCheck,
  MapPin,
  Building
} from 'lucide-react';

interface ToastItem {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message?: string;
}

interface BatchSummary {
  total_doctors: number;
  total_hours: string;
  total_deficit: string;
  total_overtime: string;
}

interface BatchItem {
  id: string;
  name: string;
  created_at: string;
  notes: string;
  date_range: string;
  date_min: string | null;
  date_max: string | null;
  files_count: number;
  master_file: string;
  auth_files: string[];
  summary: BatchSummary;
  doctors_count: number;
  is_edited?: boolean;
}

interface FilterOptions {
  sectors?: string[];
  locations_by_sector?: Record<string, string[]>;
  locations?: string[];
  departments: string[];
  contracts: string[];
  job_groups: string[];
  job_titles: string[];
  doctor_job_titles?: string[];
  terminals: string[];
  date_min: string | null;
  date_max: string | null;
}

interface DoctorItem {
  emp_code: string;
  emp_name: string;
  job_title: string;
  department: string;
  sector?: string;
  is_doctor?: boolean;
  device_locations?: string[];
  contract: string;
  total_days_worked: number;
  total_time_spent: string;
  total_deficit: string;
  total_overtime: string;
  records_count: number;
}

interface AttendanceRecord {
  date: string;
  day: string;
  check_in_1: string;
  check_out_1: string;
  check_in_2: string;
  check_out_2: string;
  time_spent: string;
  shift_type: string;
  deficit_time: string;
  overtime_time: string;
  is_deficit: boolean;
  is_overtime: boolean;
  is_late_arrival: boolean;
  time_spent_minutes?: number;
  deficit_minutes?: number;
  overtime_minutes?: number;
  key_warning?: string;
  // Punch metadata
  in_1_key?: string;
  out_1_key?: string;
  in_2_key?: string;
  out_2_key?: string;
  in_1_auth_type?: string;
  out_1_auth_type?: string;
  in_2_auth_type?: string;
  out_2_auth_type?: string;
  in_1_terminal?: string;
  out_1_terminal?: string;
  in_2_terminal?: string;
  out_2_terminal?: string;
}

interface DoctorDetail extends DoctorItem {
  records: AttendanceRecord[];
}

// Robust Arabic & English text normalization for search and filtering
function normalizeArabicEnglish(text: string | null | undefined): string {
  if (!text) return '';
  let s = String(text).trim().toLowerCase();
  s = s.replace(/[\u064B-\u065F\u0670]/g, ''); // diacritics / tashkeel
  s = s.replace(/\u0640/g, ''); // tatweel
  s = s.replace(/[أإآٱ]/g, 'ا'); // alef variations
  s = s.replace(/[ىي]/g, 'ي'); // yaa / alef maksura
  s = s.replace(/ة/g, 'ه'); // taa marbuta
  s = s.replace(/\s+/g, ' ');
  return s.trim();
}

// Direct Backend API URL resolver: avoids Next.js reverse-proxy socket timeouts on large file uploads
function getApiUrl(endpoint: string): string {
  if (typeof window !== 'undefined') {
    const host = window.location.hostname || '127.0.0.1';
    return `http://${host}:8000${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
  }
  return endpoint;
}

export default function DashboardPage() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  // Toast notifications state
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const showToast = (type: 'success' | 'error' | 'info' | 'warning', title: string, message?: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      removeToast(id);
    }, 4500);
  };

  // Batches state
  const [batches, setBatches] = useState<BatchItem[]>([]);
  const [activeBatchId, setActiveBatchId] = useState<string | null>(null);
  const [batchesLoading, setBatchesLoading] = useState(true);
  const [batchesError, setBatchesError] = useState<string | null>(null);
  const [deletingBatchId, setDeletingBatchId] = useState<string | null>(null);

  // Active batch data
  const [summary, setSummary] = useState<BatchSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [doctors, setDoctors] = useState<DoctorItem[]>([]);
  const [totalDoctors, setTotalDoctors] = useState(0);
  const [loading, setLoading] = useState(true);
  const [doctorsError, setDoctorsError] = useState<string | null>(null);

  // Filters & Pagination
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('');
  const [selectedSector, setSelectedSector] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedJobs, setSelectedJobs] = useState<string[]>([]);
  const [jobsDropdownOpen, setJobsDropdownOpen] = useState(false);
  const [jobsSearch, setJobsSearch] = useState('');
  const [onlyDoctors, setOnlyDoctors] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  // Available locations cascading from selected sector
  const availableLocations = React.useMemo(() => {
    if (selectedSector && filterOptions?.locations_by_sector?.[selectedSector]) {
      return filterOptions.locations_by_sector[selectedSector];
    }
    return filterOptions?.locations || [];
  }, [selectedSector, filterOptions]);

  // Filtered job titles based on search inside multi-select dropdown (context-aware for doctors)
  const filteredJobTitles = React.useMemo(() => {
    let list = filterOptions?.job_titles || [];
    if (onlyDoctors && filterOptions?.doctor_job_titles && filterOptions.doctor_job_titles.length > 0) {
      list = filterOptions.doctor_job_titles;
    }
    if (!jobsSearch.trim()) return list;
    const q = normalizeArabicEnglish(jobsSearch);
    return list.filter((j) => normalizeArabicEnglish(j).includes(q));
  }, [filterOptions?.job_titles, filterOptions?.doctor_job_titles, jobsSearch, onlyDoctors]);

  // Is any filter active
  const isAnyFilterActive = Boolean(
    search.trim() ||
    selectedDept.trim() ||
    (selectedSector && selectedSector !== 'جميع القطاعات') ||
    (selectedLocation && selectedLocation !== 'جميع الأماكن') ||
    selectedJobs.length > 0 ||
    onlyDoctors
  );

  // Dynamic Export URL builder: guarantees that ONLY the selected doctors are exported!
  const getExportUrl = (format: 'excel' | 'pdf') => {
    const params = new URLSearchParams();
    if (activeBatchId) params.append('batch_id', activeBatchId);
    if (search.trim()) params.append('search', search.trim());
    if (selectedDept.trim()) params.append('dept', selectedDept.trim());
    if (selectedSector && selectedSector !== 'جميع القطاعات') params.append('sector', selectedSector);
    if (selectedLocation && selectedLocation !== 'جميع الأماكن') params.append('location', selectedLocation);
    if (selectedJobs.length > 0) {
      selectedJobs.forEach((j) => params.append('jobs', j));
    }
    if (onlyDoctors) params.append('only_doctors', 'true');
    return getApiUrl(`/api/export/${format}?${params.toString()}`);
  };

  // Filter Handlers
  const handleJobToggle = (jobTitle: string) => {
    setSelectedJobs((prev) =>
      prev.includes(jobTitle) ? prev.filter((j) => j !== jobTitle) : [...prev, jobTitle]
    );
    setPage(1);
  };

  const handleSelectAllFilteredJobs = () => {
    const set = new Set([...selectedJobs, ...filteredJobTitles]);
    setSelectedJobs(Array.from(set));
    setPage(1);
  };

  const handleClearJobs = () => {
    setSelectedJobs([]);
    setJobsSearch('');
    setPage(1);
  };

  const handleSectorChange = (sec: string) => {
    setSelectedSector(sec);
    setSelectedLocation('');
    setPage(1);
  };

  const handleLocationChange = (loc: string) => {
    setSelectedLocation(loc);
    setPage(1);
  };

  const handleToggleOnlyDoctors = () => {
    setOnlyDoctors((prev) => !prev);
    setPage(1);
  };

  const handleResetAllFilters = () => {
    setSearch('');
    setSelectedDept('');
    setSelectedSector('');
    setSelectedLocation('');
    setSelectedJobs([]);
    setJobsSearch('');
    setOnlyDoctors(false);
    setPage(1);
  };

  // Modals state
  const [selectedDoctor, setSelectedDoctor] = useState<DoctorDetail | null>(null);
  const [loadingDoctorDetail, setLoadingDoctorDetail] = useState(false);
  const [activeDoctorCode, setActiveDoctorCode] = useState<string | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedRecords, setEditedRecords] = useState<AttendanceRecord[]>([]);
  const [savingEdit, setSavingEdit] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [selectedAlertRecord, setSelectedAlertRecord] = useState<{ record: AttendanceRecord; docName: string; empCode: string } | null>(null);

  // New batch modal
  const [showNewBatchModal, setShowNewBatchModal] = useState(false);
  const [newBatchName, setNewBatchName] = useState('');
  const [newBatchNotes, setNewBatchNotes] = useState('');
  const [newMasterFiles, setNewMasterFiles] = useState<FileList | null>(null);
  const [newAuthFiles, setNewAuthFiles] = useState<FileList | null>(null);
  const [uploadingNew, setUploadingNew] = useState(false);

  // Append files modal
  const [showAppendModal, setShowAppendModal] = useState(false);
  const [appendAuthFiles, setAppendAuthFiles] = useState<FileList | null>(null);
  const [appendMasterFiles, setAppendMasterFiles] = useState<FileList | null>(null);
  const [appending, setAppending] = useState(false);

  // Toggle Theme
  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
  };

  // Fetch active batch details
  const fetchActiveBatchData = async (batchId: string) => {
    try {
      setSummaryLoading(true);
      const [sumRes, optRes] = await Promise.all([
        fetch(getApiUrl(`/api/summary?batch_id=${batchId}`)),
        fetch(getApiUrl(`/api/filter-options?batch_id=${batchId}`))
      ]);

      if (sumRes.ok) setSummary(await sumRes.json());
      if (optRes.ok) setFilterOptions(await optRes.json());
    } catch (err) {
      console.error('Error fetching batch data:', err);
    } finally {
      setSummaryLoading(false);
    }
  };

  // Fetch doctors list with multi-criteria filtering
  const fetchDoctors = async (
    targetBatchId?: string,
    targetPage?: number,
    targetPageSize?: number,
    targetSearch?: string,
    targetDept?: string,
    targetSector?: string,
    targetLocation?: string,
    targetJobs?: string[],
    targetOnlyDoctors?: boolean
  ) => {
    const bId = targetBatchId || activeBatchId;
    if (!bId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setDoctorsError(null);
      const curPage = targetPage !== undefined ? targetPage : page;
      const curLimit = targetPageSize !== undefined ? targetPageSize : pageSize;
      const curSearch = targetSearch !== undefined ? targetSearch : search;
      const curDept = targetDept !== undefined ? targetDept : selectedDept;
      const curSector = targetSector !== undefined ? targetSector : selectedSector;
      const curLocation = targetLocation !== undefined ? targetLocation : selectedLocation;
      const curJobs = targetJobs !== undefined ? targetJobs : selectedJobs;
      const curOnlyDoctors = targetOnlyDoctors !== undefined ? targetOnlyDoctors : onlyDoctors;

      const params = new URLSearchParams();
      params.append('batch_id', bId);
      if (curSearch.trim()) params.append('search', curSearch.trim());
      if (curDept.trim()) params.append('dept', curDept.trim());
      if (curSector.trim() && curSector !== 'جميع القطاعات') params.append('sector', curSector.trim());
      if (curLocation.trim() && curLocation !== 'جميع الأماكن') params.append('location', curLocation.trim());
      if (curJobs && curJobs.length > 0) {
        curJobs.forEach((j) => params.append('jobs', j));
      }
      if (curOnlyDoctors) params.append('only_doctors', 'true');

      params.append('limit', String(curLimit));
      params.append('offset', String((curPage - 1) * curLimit));

      const res = await fetch(getApiUrl(`/api/doctors?${params.toString()}`));
      if (res.ok) {
        const data = await res.json();
        setDoctors(data.doctors || []);
        setTotalDoctors(data.total || 0);
      } else {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `فشل تحميل قائمة الموظفين (رمز ${res.status})`);
      }
    } catch (err: any) {
      console.error('Error fetching doctors:', err);
      setDoctorsError(err.message || 'حدث خطأ أثناء تحميل سجلات الموظفين من الخادم.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch batches with loading & error states
  const fetchBatches = async () => {
    try {
      setBatchesLoading(true);
      setBatchesError(null);
      const res = await fetch(getApiUrl('/api/batches'));
      if (res.ok) {
        const data = await res.json();
        setBatches(data.batches || []);
        if (!activeBatchId && data.active_batch_id) {
          setActiveBatchId(data.active_batch_id);
          fetchActiveBatchData(data.active_batch_id);
          fetchDoctors(data.active_batch_id, 1, pageSize, '', '');
        }
      } else {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `فشل جلب قائمة الدفعات (رمز ${res.status})`);
      }
    } catch (err: any) {
      console.error('Error fetching batches:', err);
      setBatchesError(err.message || 'تعذر الاتصال بالخادم لجلب سجل الدفعات.');
    } finally {
      setBatchesLoading(false);
    }
  };

  useEffect(() => {
    fetchBatches();
  }, []);

  useEffect(() => {
    if (activeBatchId) {
      fetchActiveBatchData(activeBatchId);
    }
  }, [activeBatchId]);

  // Debounced live fetch on any filter or page change
  useEffect(() => {
    const debounce = setTimeout(() => {
      fetchDoctors(
        activeBatchId || undefined,
        page,
        pageSize,
        search,
        selectedDept,
        selectedSector,
        selectedLocation,
        selectedJobs,
        onlyDoctors
      );
    }, 250);
    return () => clearTimeout(debounce);
  }, [search, selectedDept, selectedSector, selectedLocation, selectedJobs, onlyDoctors, page, pageSize]);

  // Switch batch - updates all screen states smoothly and synchronously
  const handleSelectBatch = async (batchId: string) => {
    if (batchId === activeBatchId) return;
    try {
      setLoading(true);
      setActiveBatchId(batchId);
      handleResetAllFilters();

      const res = await fetch(getApiUrl(`/api/batches/${batchId}/activate`), { method: 'POST' });
      if (res.ok) {
        await Promise.all([
          fetchBatches(),
          fetchActiveBatchData(batchId),
          fetchDoctors(batchId, 1, pageSize, '', '')
        ]);
        const target = batches.find((b) => b.id === batchId);
        showToast('info', 'تم تفعيل الدفعة', target ? target.name : 'تم تحديد الدفعة بنجاح');
      } else {
        const err = await res.json().catch(() => ({}));
        showToast('error', 'فشل تفعيل الدفعة', err.detail || 'تعذر تعيين الدفعة كنشطة.');
      }
    } catch (err: any) {
      console.error('Error activating batch:', err);
      showToast('error', 'خطأ في الاتصال', 'تعذر إرسال طلب تفعيل الدفعة.');
    } finally {
      setLoading(false);
    }
  };

  // Delete batch
  const handleDeleteBatch = async (batchId: string, name: string) => {
    if (!confirm(`هل أنت متأكد من حذف الدفعة: "${name}" من الأرشيف؟`)) return;
    try {
      setDeletingBatchId(batchId);
      const res = await fetch(getApiUrl(`/api/batches/${batchId}`), { method: 'DELETE' });
      if (res.ok) {
        if (activeBatchId === batchId) {
          setActiveBatchId(null);
          setSummary(null);
          setDoctors([]);
        }
        showToast('success', 'تم حذف الدفعة', `تمت إزالة "${name}" من الأرشيف بنجاح.`);
        fetchBatches();
      } else {
        const err = await res.json().catch(() => ({}));
        showToast('error', 'فشل حذف الدفعة', err.detail || 'تعذر حذف الدفعة من السيرفر.');
      }
    } catch (err: any) {
      console.error('Error deleting batch:', err);
      showToast('error', 'خطأ في الاتصال', 'تعذر إتمام طلب حذف الدفعة.');
    } finally {
      setDeletingBatchId(null);
    }
  };

  // Open doctor detail modal
  const openDoctorModal = async (empCode: string) => {
    if (!activeBatchId) return;
    try {
      setActiveDoctorCode(empCode);
      setLoadingDoctorDetail(true);
      const res = await fetch(getApiUrl(`/api/doctors/${empCode}?batch_id=${activeBatchId}`));
      if (res.ok) {
        const docData = await res.json();
        setSelectedDoctor(docData);
        setEditedRecords(JSON.parse(JSON.stringify(docData.records || [])));
        setIsEditMode(false);
        setSaveSuccess(false);
      } else {
        const err = await res.json().catch(() => ({}));
        showToast('error', 'تعذر فتح كشف الموظف', err.detail || 'لم يتم العثور على سجلات الموظف في هذه الدفعة.');
      }
    } catch (err: any) {
      console.error('Error loading doctor detail:', err);
      showToast('error', 'خطأ في الاتصال', 'تعذر جلب تفاصيل الموظف من الخادم.');
    } finally {
      setLoadingDoctorDetail(false);
      setActiveDoctorCode(null);
    }
  };

  // Handle Edit Records Change
  const handleRecordChange = (index: number, field: keyof AttendanceRecord, value: any) => {
    const updated = [...editedRecords];
    updated[index] = { ...updated[index], [field]: value };
    setEditedRecords(updated);
  };

  // Add new day row to doctor records
  const handleAddDayRow = () => {
    const newRow: AttendanceRecord = {
      date: new Date().toISOString().split('T')[0],
      day: 'السبت',
      check_in_1: '08:30 AM',
      check_out_1: '02:30 PM',
      check_in_2: '',
      check_out_2: '',
      time_spent: '6:00',
      shift_type: 'A',
      deficit_time: '0:00',
      overtime_time: '0:00',
      is_deficit: false,
      is_overtime: false,
      is_late_arrival: false,
      time_spent_minutes: 360,
      deficit_minutes: 0,
      overtime_minutes: 0
    };
    setEditedRecords([...editedRecords, newRow]);
  };

  // Delete day row
  const handleDeleteDayRow = (index: number) => {
    const updated = editedRecords.filter((_, idx) => idx !== index);
    setEditedRecords(updated);
  };

  // Save manual edits to backend with immediate optimistic UI update & server sync
  const handleSaveEdits = async () => {
    if (!activeBatchId || !selectedDoctor) return;
    try {
      setSavingEdit(true);
      const res = await fetch(getApiUrl(`/api/batches/${activeBatchId}/doctors/${selectedDoctor.emp_code}`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ records: editedRecords })
      });

      if (res.ok) {
        const data = await res.json();
        
        // 1. Immediately update modal state and close edit mode
        setSelectedDoctor(data.doctor);
        setEditedRecords(JSON.parse(JSON.stringify(data.doctor.records || [])));
        setSaveSuccess(true);
        setIsEditMode(false);

        // 2. Immediately update batch summary cards if returned
        if (data.batch_summary) {
          setSummary(data.batch_summary);
        }

        // 3. Immediately update doctor item in table state for instant feedback
        setDoctors((prev) => prev.map((doc) => {
          if (doc.emp_code === data.doctor.emp_code) {
            return {
              ...doc,
              total_days_worked: data.doctor.total_days_worked,
              total_time_spent: data.doctor.total_time_spent,
              total_deficit: data.doctor.total_deficit,
              total_overtime: data.doctor.total_overtime,
              records_count: (data.doctor.records || []).length
            };
          }
          return doc;
        }));

        showToast('success', 'تم حفظ التعديلات بنجاح', `تم تحديث كشف الطبيب: ${selectedDoctor.emp_name} وإعادة احتساب المجاميع.`);

        // 4. Concurrently sync full server state in background
        await Promise.all([
          fetchBatches(),
          fetchActiveBatchData(activeBatchId),
          fetchDoctors(activeBatchId, page, pageSize, search, selectedDept)
        ]);
      } else {
        const err = await res.json().catch(() => ({}));
        showToast('error', 'فشل حفظ التعديلات', err.detail || 'حدث خطأ أثناء حفظ التعديلات في الخادم.');
      }
    } catch (err: any) {
      console.error('Error saving edits:', err);
      showToast('error', 'خطأ في الشبكة', 'تعذر الاتصال بالخادم لحفظ التعديلات.');
    } finally {
      setSavingEdit(false);
    }
  };

  // Handle new batch submission with clean UI reset & full synchronization
  const handleNewBatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setUploadingNew(true);
      const formData = new FormData();
      const defaultName = `دفعة استيراد ${new Date().toLocaleDateString('ar-EG')} (${new Date().toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })})`;
      formData.append('batch_name', newBatchName.trim() || defaultName);
      if (newBatchNotes.trim()) formData.append('notes', newBatchNotes.trim());

      if (newMasterFiles && newMasterFiles.length > 0) {
        for (let i = 0; i < newMasterFiles.length; i++) {
          formData.append('master_files', newMasterFiles[i]);
        }
      }

      if (newAuthFiles && newAuthFiles.length > 0) {
        for (let i = 0; i < newAuthFiles.length; i++) {
          formData.append('auth_files', newAuthFiles[i]);
        }
      }

      const res = await fetch(getApiUrl('/api/batches'), {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();

        // 1. Reset modal inputs and close
        setShowNewBatchModal(false);
        setNewBatchName('');
        setNewBatchNotes('');
        setNewMasterFiles(null);
        setNewAuthFiles(null);

        // 2. Reset workspace search filters & pagination
        setSelectedDoctor(null);
        setSearch('');
        setSelectedDept('');
        setPage(1);
        setActiveBatchId(data.batch.id);

        showToast('success', 'تم استيراد الدفعة بنجاح', `تم إنشاء الدفعة "${data.batch?.name || ''}" وتوثيق ${data.batch?.doctors_count || 0} موظف.`);

        // 3. Concurrently load new batch batches, KPI summary, and doctors table
        await Promise.all([
          fetchBatches(),
          fetchActiveBatchData(data.batch.id),
          fetchDoctors(data.batch.id, 1, pageSize, '', '')
        ]);
      } else {
        const err = await res.json().catch(() => ({}));
        showToast('error', 'فشل استيراد الدفعة', err.detail || 'حدث خطأ أثناء معالجة ملفات البصمة.');
      }
    } catch (err: any) {
      console.error('Error creating batch:', err);
      showToast('error', 'خطأ أثناء الرفع', 'تعذر إرسال الملفات إلى الخادم.');
    } finally {
      setUploadingNew(false);
    }
  };

  // Handle appending files to existing batch with unified UI re-synchronization
  const handleAppendFilesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeBatchId || !appendAuthFiles || appendAuthFiles.length === 0) {
      showToast('warning', 'تنبيه', 'يرجى اختيار ملفات البصمة الإضافية أولاً.');
      return;
    }

    try {
      setAppending(true);
      const formData = new FormData();
      for (let i = 0; i < appendAuthFiles.length; i++) {
        formData.append('auth_files', appendAuthFiles[i]);
      }
      if (appendMasterFiles && appendMasterFiles.length > 0) {
        for (let i = 0; i < appendMasterFiles.length; i++) {
          formData.append('master_files', appendMasterFiles[i]);
        }
      }

      const res = await fetch(getApiUrl(`/api/batches/${activeBatchId}/append-files`), {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        // 1. Close append modal and reset file pickers
        setShowAppendModal(false);
        setAppendAuthFiles(null);
        setAppendMasterFiles(null);

        showToast('success', 'تم دمج الملفات بنجاح', 'تمت إضافة ملفات البصمة وإعادة احتساب الحضور والانصراف والعجز.');

        // 2. Concurrently refresh all batches, active batch KPIs, and table
        await Promise.all([
          fetchBatches(),
          fetchActiveBatchData(activeBatchId),
          fetchDoctors(activeBatchId, page, pageSize, search, selectedDept)
        ]);

        // 3. Refresh opened doctor detail modal if active
        if (selectedDoctor) {
          openDoctorModal(selectedDoctor.emp_code);
        }
      } else {
        const err = await res.json().catch(() => ({}));
        showToast('error', 'فشل دمج الملفات', err.detail || 'حدث خطأ أثناء معالجة الملفات الملحقة.');
      }
    } catch (err: any) {
      console.error('Error appending files:', err);
      showToast('error', 'خطأ أثناء الإلحاق', 'تعذر إرسال الملفات الإضافية إلى الخادم.');
    } finally {
      setAppending(false);
    }
  };

  const activeBatch = batches.find((b) => b.id === activeBatchId);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

      {/* 1. TOP NAVBAR */}
      <header className="glass" style={{ position: 'sticky', top: 0, zIndex: 40, borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ padding: '14px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>

          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{
              width: 46,
              height: 46,
              borderRadius: 'var(--radius-md)',
              background: '#ffffff',
              padding: 3,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-glow)',
              overflow: 'hidden',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <img
                src="/logo.svg"
                alt="MSC Logo"
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/logo.jpeg';
                }}
              />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <h1 style={{ fontSize: '1.15rem', fontWeight: 800, letterSpacing: '-0.02em' }}>شركة الخدمات الطبية - مستشفى الكهرباء</h1>
                <span className="badge badge-blue">إدارة نظم المعلومات والتحول الرقمي</span>
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 2 }}>
                منظومة ذكاء بصمات الأطباء والعاملين (MSC Fingerprint & Deficit Intelligence)
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button onClick={() => setShowNewBatchModal(true)} className="btn-primary">
              <PlusCircle size={17} />
              <span>استيراد دفعة جديدة</span>
            </button>

            <a
              href={getExportUrl('excel')}
              download
              className="btn-secondary"
              style={{
                textDecoration: 'none',
                borderColor: isAnyFilterActive ? '#10B981' : undefined,
                background: isAnyFilterActive ? 'rgba(16, 185, 129, 0.14)' : undefined,
                color: isAnyFilterActive ? '#10B981' : undefined,
                fontWeight: isAnyFilterActive ? 700 : 500
              }}
              title={isAnyFilterActive ? `تصدير بيانات ${totalDoctors} موظف محددين إلى Excel` : 'تصدير إكسيل الدفعة كاملة'}
            >
              <FileSpreadsheet size={17} color="#10B981" />
              <span>{isAnyFilterActive ? `Excel المحدد (${totalDoctors})` : 'Excel الدفعة'}</span>
            </a>

            <a
              href={getExportUrl('pdf')}
              download
              className="btn-secondary"
              style={{
                textDecoration: 'none',
                borderColor: isAnyFilterActive ? '#EF4444' : undefined,
                background: isAnyFilterActive ? 'rgba(239, 68, 68, 0.14)' : undefined,
                color: isAnyFilterActive ? '#EF4444' : undefined,
                fontWeight: isAnyFilterActive ? 700 : 500
              }}
              title={isAnyFilterActive ? `تصدير بيانات ${totalDoctors} موظف محددين إلى PDF` : 'تصدير PDF الدفعة كاملة'}
            >
              <FileText size={17} color="#EF4444" />
              <span>{isAnyFilterActive ? `PDF المحدد (${totalDoctors})` : 'PDF الدفعة'}</span>
            </a>

            <button onClick={toggleTheme} className="btn-secondary" title="تبديل المظهر">
              {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
            </button>
          </div>

        </div>
      </header>

      {/* 2. MASTER-DETAIL BODY LAYOUT */}
      <div style={{ display: 'flex', flex: 1, minHeight: 'calc(100vh - 72px)', overflow: 'hidden' }}>

        {/* 2.1 RIGHT SIDEBAR: BATCHES LIST WITH TIME AND DATE */}
        <aside className="glass" style={{ width: 340, borderLeft: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', background: 'var(--bg-secondary)' }}>

          <div style={{ padding: '16px 18px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <FolderArchive size={18} color="#818CF8" />
              <h2 style={{ fontSize: '1rem', fontWeight: 700 }}>سجل الدفعات ({batches.length})</h2>
            </div>
            <button
              onClick={() => setShowNewBatchModal(true)}
              className="btn-primary"
              style={{ padding: '6px 10px', fontSize: '0.8rem' }}
              title="إضافة دفعة أسبوعية جديدة"
            >
              <Plus size={15} />
              <span>جديدة</span>
            </button>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', padding: 12, display: 'flex', flexDirection: 'column', gap: 10 }}>
            {batchesLoading ? (
              // Batches Loading Skeletons
              [1, 2, 3].map((i) => (
                <div key={i} className="glass" style={{ padding: 14, borderRadius: 'var(--radius-md)' }}>
                  <div className="skeleton" style={{ height: 16, width: '75%', marginBottom: 10 }} />
                  <div className="skeleton" style={{ height: 12, width: '55%', marginBottom: 10 }} />
                  <div style={{ display: 'flex', gap: 6 }}>
                    <div className="skeleton" style={{ height: 18, width: 60 }} />
                    <div className="skeleton" style={{ height: 18, width: 50 }} />
                  </div>
                </div>
              ))
            ) : batchesError ? (
              // Batches Error State
              <div style={{ padding: 16, borderRadius: 'var(--radius-md)', background: 'var(--danger-bg)', border: '1px solid rgba(239, 68, 68, 0.3)', textAlign: 'center' }}>
                <AlertCircle size={24} color="#f87171" style={{ margin: '0 auto 8px' }} />
                <p style={{ fontSize: '0.82rem', color: 'var(--danger-text)', marginBottom: 12, lineHeight: 1.5 }}>
                  {batchesError}
                </p>
                <button
                  onClick={fetchBatches}
                  className="btn-secondary"
                  style={{ padding: '5px 12px', fontSize: '0.78rem', margin: '0 auto' }}
                >
                  <RefreshCw size={12} />
                  <span>إعادة المحاولة</span>
                </button>
              </div>
            ) : batches.length === 0 ? (
              // Batches Empty State
              <div style={{ padding: '28px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <FolderArchive size={28} style={{ opacity: 0.4, margin: '0 auto 10px' }} />
                <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>لا توجد دفعات محفوظة</p>
                <p style={{ fontSize: '0.78rem', marginBottom: 14 }}>قم باستيراد أول دفعة بصمات لبدء التحليل.</p>
                <button
                  onClick={() => setShowNewBatchModal(true)}
                  className="btn-primary"
                  style={{ padding: '6px 12px', fontSize: '0.78rem', margin: '0 auto' }}
                >
                  <Plus size={13} />
                  <span>استيراد دفعة جديدة</span>
                </button>
              </div>
            ) : (
              batches.map((b) => {
                const isActive = b.id === activeBatchId;
                const isDeleting = deletingBatchId === b.id;
                return (
                  <div
                    key={b.id}
                    onClick={() => handleSelectBatch(b.id)}
                    className="glass-hover"
                    style={{
                      padding: 14,
                      borderRadius: 'var(--radius-md)',
                      cursor: 'pointer',
                      border: isActive ? '2px solid var(--accent-blue)' : '1px solid var(--border-color)',
                      background: isActive ? 'rgba(59, 130, 246, 0.08)' : 'var(--bg-card)',
                      transition: 'all 0.2s ease',
                      opacity: isDeleting ? 0.5 : 1
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                      <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: isActive ? 'var(--accent-blue)' : 'var(--text-primary)' }}>
                        {b.name}
                      </h3>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDeleteBatch(b.id, b.name); }}
                        disabled={isDeleting}
                        style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: isDeleting ? 'not-allowed' : 'pointer', padding: 2 }}
                        title="حذف الدفعة"
                      >
                        {isDeleting ? <RefreshCw size={14} className="animate-spin" /> : <Trash2 size={14} />}
                      </button>
                    </div>

                    {/* Timestamp & Date */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 6 }}>
                      <CalendarClock size={13} />
                      <span>استيراد: {b.created_at}</span>
                    </div>

                    {/* Date Range */}
                    {b.date_range && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: 8 }}>
                        الفترة: {b.date_range}
                      </div>
                    )}

                    {/* Stats Badges */}
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      <span className="badge badge-blue" style={{ fontSize: '0.7rem' }}>
                        {b.doctors_count} موظف
                      </span>
                      <span className="badge" style={{ fontSize: '0.7rem', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)' }}>
                        {b.files_count} ملفات
                      </span>
                      {b.is_edited && (
                        <span className="badge badge-peach" style={{ fontSize: '0.7rem' }}>
                          معدلة يدوياً
                        </span>
                      )}
                    </div>

                  </div>
                );
              })
            )}
          </div>

        </aside>

        {/* 2.2 MAIN CONTENT WORKSPACE: ACTIVE BATCH DATA */}
        <main style={{ flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column' }}>

          {/* Active Batch Header Bar */}
          {activeBatch ? (
            <div className="glass animate-fade-in" style={{ padding: '16px 20px', borderRadius: 'var(--radius-lg)', marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 14 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>{activeBatch.name}</h2>
                  {activeBatch.is_edited && (
                    <span className="badge badge-peach">تم إجراء تعديلات يدوية</span>
                  )}
                </div>
                <div style={{ display: 'flex', gap: 16, fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
                  <span>تاريخ وتوقيت الرفع: {activeBatch.created_at}</span>
                  {activeBatch.date_range && <span>نطاق البصمات: {activeBatch.date_range}</span>}
                  <span>الملفات المرتبطة: {activeBatch.files_count} ملف</span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                <button onClick={() => setShowAppendModal(true)} className="btn-secondary" style={{ borderColor: 'var(--accent-blue)', color: 'var(--accent-blue)' }}>
                  <FilePlus2 size={16} />
                  <span>إضافة ملفات لهذه الدفعة</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="glass" style={{ padding: 20, borderRadius: 'var(--radius-lg)', marginBottom: 20, textAlign: 'center', color: 'var(--text-muted)' }}>
              يرجى اختيار دفعة من القائمة الجانبية أو استيراد دفعة جديدة.
            </div>
          )}

          {/* KPI STATS CARDS */}
          <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 20 }}>

            <div className="glass glass-hover animate-fade-in" style={{ padding: 18, borderRadius: 'var(--radius-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>إجمالي الأطباء والموظفين</span>
                <div style={{ width: 34, height: 34, borderRadius: 'var(--radius-sm)', background: 'rgba(59, 130, 246, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#60A5FA' }}>
                  <Users size={18} />
                </div>
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800 }}>
                {summaryLoading ? (
                  <div className="skeleton" style={{ height: 32, width: 90, marginTop: 4, marginBottom: 4 }} />
                ) : summary ? (
                  `${summary.total_doctors} موظف`
                ) : (
                  '...'
                )}
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>سجلات الدفعة الحالية</span>
            </div>

            <div className="glass glass-hover animate-fade-in" style={{ padding: 18, borderRadius: 'var(--radius-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>إجمالي الساعات المقضية</span>
                <div style={{ width: 34, height: 34, borderRadius: 'var(--radius-sm)', background: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#818CF8' }}>
                  <Clock size={18} />
                </div>
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800 }}>
                {summaryLoading ? (
                  <div className="skeleton" style={{ height: 32, width: 85, marginTop: 4, marginBottom: 4 }} />
                ) : summary ? (
                  `${summary.total_hours} س`
                ) : (
                  '...'
                )}
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>مجموع الوقت الفعلي</span>
            </div>

            <div className="glass glass-hover animate-fade-in" style={{ padding: 18, borderRadius: 'var(--radius-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>إجمالي ساعات العجز / التأخير</span>
                <div style={{ width: 34, height: 34, borderRadius: 'var(--radius-sm)', background: 'var(--peach-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--peach-text)' }}>
                  <AlertTriangle size={18} />
                </div>
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--peach-text)' }}>
                {summaryLoading ? (
                  <div className="skeleton" style={{ height: 32, width: 85, marginTop: 4, marginBottom: 4 }} />
                ) : summary ? (
                  `${summary.total_deficit} س`
                ) : (
                  '...'
                )}
              </div>
              <span className="badge badge-peach" style={{ marginTop: 4 }}>عجز الشفتات المستهدفة</span>
            </div>

            <div className="glass glass-hover animate-fade-in" style={{ padding: 18, borderRadius: 'var(--radius-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>إجمالي الساعات الإضافية</span>
                <div style={{ width: 34, height: 34, borderRadius: 'var(--radius-sm)', background: 'var(--mint-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--mint-text)' }}>
                  <Award size={18} />
                </div>
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--mint-text)' }}>
                {summaryLoading ? (
                  <div className="skeleton" style={{ height: 32, width: 85, marginTop: 4, marginBottom: 4 }} />
                ) : summary ? (
                  `${summary.total_overtime} س`
                ) : (
                  '...'
                )}
              </div>
              <span className="badge badge-mint" style={{ marginTop: 4 }}>الساعات الإضافية المستحقة</span>
            </div>

          </section>

          {/* DYNAMIC FILTER BAR */}
          <section className="glass" style={{ padding: 18, borderRadius: 'var(--radius-lg)', marginBottom: 20, position: 'relative', zIndex: 30 }}>
            {/* Top Row: Primary Selectors */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center' }}>

              {/* 1. Live Search */}
              <div style={{ position: 'relative', minWidth: 220, flex: 1 }}>
                <Search size={16} style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  placeholder="ابحث بالاسم، الكود، الوظيفة..."
                  value={search}
                  onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                  style={{
                    width: '100%',
                    padding: '9px 38px 9px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-main)',
                    fontSize: '0.84rem'
                  }}
                />
                {search && (
                  <button
                    onClick={() => { setSearch(''); setPage(1); }}
                    style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                  >
                    <X size={14} />
                  </button>
                )}
              </div>

              {/* 2. Sector Selector (القطاع) */}
              <div style={{ minWidth: 190, flex: 1, position: 'relative' }}>
                <select
                  value={selectedSector}
                  onChange={(e) => handleSectorChange(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-secondary)',
                    border: selectedSector ? '1px solid var(--accent-blue)' : '1px solid var(--border-color)',
                    color: selectedSector ? 'var(--accent-blue)' : 'var(--text-primary)',
                    fontFamily: 'var(--font-main)',
                    fontSize: '0.84rem',
                    fontWeight: selectedSector ? 600 : 400
                  }}
                >
                  <option value="">القطاع: الكل ({filterOptions?.sectors?.length || 0})</option>
                  {(filterOptions?.sectors || []).map((sec) => (
                    <option key={sec} value={sec}>{sec}</option>
                  ))}
                </select>
              </div>

              {/* 3. Location Selector (المكان / المستشفى) */}
              <div style={{ minWidth: 200, flex: 1 }}>
                <select
                  value={selectedLocation}
                  onChange={(e) => handleLocationChange(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-secondary)',
                    border: selectedLocation ? '1px solid var(--accent-blue)' : '1px solid var(--border-color)',
                    color: selectedLocation ? 'var(--accent-blue)' : 'var(--text-primary)',
                    fontFamily: 'var(--font-main)',
                    fontSize: '0.84rem',
                    fontWeight: selectedLocation ? 600 : 400
                  }}
                >
                  <option value="">
                    {selectedSector ? `أماكن ${selectedSector} (${availableLocations.length})` : `المكان: الكل (${availableLocations.length})`}
                  </option>
                  {availableLocations.map((loc) => (
                    <option key={loc} value={loc}>{loc}</option>
                  ))}
                </select>
              </div>

              {/* 4. Multi-Select Job Title (الوظيفة) */}
              <div style={{ position: 'relative', minWidth: 220, flex: 1 }}>
                <button
                  type="button"
                  onClick={() => setJobsDropdownOpen(!jobsDropdownOpen)}
                  className="btn-secondary"
                  style={{
                    width: '100%',
                    justifyContent: 'space-between',
                    padding: '9px 12px',
                    fontSize: '0.84rem',
                    borderColor: selectedJobs.length > 0 ? 'var(--accent-blue)' : undefined,
                    background: selectedJobs.length > 0 ? 'rgba(59, 130, 246, 0.1)' : undefined,
                    color: selectedJobs.length > 0 ? 'var(--accent-blue)' : undefined,
                    fontWeight: selectedJobs.length > 0 ? 600 : 400
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    <Layers size={15} />
                    <span>
                      {selectedJobs.length === 0
                        ? `الوظيفة: الكل (${(onlyDoctors && filterOptions?.doctor_job_titles ? filterOptions.doctor_job_titles.length : filterOptions?.job_titles?.length) || 0})`
                        : selectedJobs.length === 1
                        ? `الوظيفة: ${selectedJobs[0]}`
                        : `الوظائف: (${selectedJobs.length}) محددة`}
                    </span>
                  </div>
                  <ChevronDown size={14} style={{ transform: jobsDropdownOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                </button>

                {/* Dropdown Floating Popover */}
                {jobsDropdownOpen && (
                  <>
                    <div
                      style={{ position: 'fixed', inset: 0, zIndex: 90 }}
                      onClick={() => setJobsDropdownOpen(false)}
                    />
                    <div
                      className="glass animate-fade-in"
                      style={{
                        position: 'absolute',
                        top: '100%',
                        right: 0,
                        marginTop: 6,
                        width: 320,
                        maxWidth: '90vw',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        borderRadius: 'var(--radius-md)',
                        boxShadow: '0 16px 40px rgba(0, 0, 0, 0.55)',
                        zIndex: 100,
                        padding: 12,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 10
                      }}
                    >
                      {/* Search inside jobs */}
                      <div style={{ position: 'relative' }}>
                        <Search size={14} style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                        <input
                          type="text"
                          placeholder="ابحث في مسميات الوظائف..."
                          value={jobsSearch}
                          onChange={(e) => setJobsSearch(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '7px 32px 7px 10px',
                            borderRadius: 'var(--radius-sm)',
                            background: 'var(--bg-secondary)',
                            border: '1px solid var(--border-color)',
                            color: 'var(--text-primary)',
                            fontSize: '0.8rem'
                          }}
                        />
                      </div>

                      {/* Select All / Clear Row */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', borderBottom: '1px solid var(--border-color)', paddingBottom: 6 }}>
                        <button
                          type="button"
                          onClick={handleSelectAllFilteredJobs}
                          style={{ background: 'none', border: 'none', color: 'var(--accent-blue)', cursor: 'pointer', fontWeight: 600 }}
                        >
                          تحديد الكل ({filteredJobTitles.length})
                        </button>
                        {selectedJobs.length > 0 && (
                          <button
                            type="button"
                            onClick={handleClearJobs}
                            style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }}
                          >
                            إلغاء التحديد
                          </button>
                        )}
                      </div>

                      {/* Scrollable list of jobs */}
                      <div style={{ maxHeight: 220, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 4 }}>
                        {filteredJobTitles.length === 0 ? (
                          <div style={{ padding: 12, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.78rem' }}>
                            لا توجد وظائف مطابقة للبحث
                          </div>
                        ) : (
                          filteredJobTitles.map((jobTitle) => {
                            const isChecked = selectedJobs.includes(jobTitle);
                            return (
                              <label
                                key={jobTitle}
                                style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 8,
                                  padding: '6px 8px',
                                  borderRadius: 'var(--radius-sm)',
                                  cursor: 'pointer',
                                  background: isChecked ? 'rgba(59, 130, 246, 0.12)' : 'transparent',
                                  fontSize: '0.8rem',
                                  color: isChecked ? 'var(--accent-blue)' : 'var(--text-primary)',
                                  fontWeight: isChecked ? 600 : 400
                                }}
                              >
                                <input
                                  type="checkbox"
                                  checked={isChecked}
                                  onChange={() => handleJobToggle(jobTitle)}
                                  style={{ accentColor: 'var(--accent-blue)', cursor: 'pointer' }}
                                />
                                <span style={{ flex: 1 }}>{jobTitle}</span>
                              </label>
                            );
                          })
                        )}
                      </div>

                      {/* Popover footer */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: 8 }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          تم تحديد: <strong style={{ color: 'var(--accent-blue)' }}>{selectedJobs.length}</strong>
                        </span>
                        <button
                          type="button"
                          onClick={() => setJobsDropdownOpen(false)}
                          className="btn-primary"
                          style={{ padding: '4px 12px', fontSize: '0.78rem' }}
                        >
                          تم
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* 5. Doctors Only Toggle Button */}
              <button
                type="button"
                onClick={handleToggleOnlyDoctors}
                className={onlyDoctors ? "btn-primary" : "btn-secondary"}
                style={{
                  padding: '9px 14px',
                  fontSize: '0.82rem',
                  borderColor: onlyDoctors ? '#10B981' : undefined,
                  background: onlyDoctors ? 'rgba(16, 185, 129, 0.18)' : undefined,
                  color: onlyDoctors ? '#10B981' : undefined,
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6
                }}
                title="تصفية وإظهار الأطباء والاستشاريين والمقيمين فقط"
              >
                <UserCheck size={16} />
                <span>الأطباء فقط</span>
                {onlyDoctors && (
                  <span className="badge badge-mint" style={{ padding: '1px 6px', fontSize: '0.68rem' }}>
                    مفعل
                  </span>
                )}
              </button>

              {/* 6. Reset Filters Button */}
              {isAnyFilterActive && (
                <button
                  type="button"
                  onClick={handleResetAllFilters}
                  className="btn-secondary"
                  style={{
                    padding: '8px 12px',
                    fontSize: '0.8rem',
                    color: 'var(--peach-text)',
                    borderColor: 'rgba(245, 157, 86, 0.4)',
                    background: 'var(--peach-bg)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6
                  }}
                  title="إلغاء جميع الفلاتر المطبقة"
                >
                  <FilterX size={15} />
                  <span>إعادة ضبط الفلاتر</span>
                </button>
              )}

            </div>

            {/* Bottom Row: Selected Jobs Tags */}
            {selectedJobs.length > 0 && (
              <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--border-color)', display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                  الوظائف المحددة ({selectedJobs.length}):
                </span>
                {selectedJobs.map((job) => (
                  <span
                    key={job}
                    className="badge badge-blue"
                    style={{ padding: '3px 8px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 4 }}
                  >
                    <span>{job}</span>
                    <button
                      type="button"
                      onClick={() => handleJobToggle(job)}
                      style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', padding: 0, display: 'flex' }}
                      title={`إزالة فلتر ${job}`}
                    >
                      <X size={12} />
                    </button>
                  </span>
                ))}
                <button
                  type="button"
                  onClick={handleClearJobs}
                  style={{ background: 'none', border: 'none', color: '#f87171', fontSize: '0.75rem', cursor: 'pointer', textDecoration: 'underline', marginRight: 4 }}
                >
                  مسح جميع الوظائف
                </button>
              </div>
            )}
          </section>

          {/* DOCTORS TABLE */}
          <section className="glass" style={{ borderRadius: 'var(--radius-lg)', overflow: 'hidden', flex: 1, position: 'relative', zIndex: 1 }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>
                  كشوف الموظفين والأطباء بالدفعة ({doctors.length} معروض من إجمالي {totalDoctors} مطابق)
                </h3>
                {isAnyFilterActive && (
                  <span className="badge badge-blue" style={{ fontSize: '0.75rem' }}>
                    نتائج التصفية الحالية
                  </span>
                )}
              </div>

              {/* Table Header Quick Export & Refresh */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <a
                  href={getExportUrl('excel')}
                  download
                  className="btn-secondary"
                  style={{
                    textDecoration: 'none',
                    padding: '5px 10px',
                    fontSize: '0.8rem',
                    borderColor: isAnyFilterActive ? '#10B981' : undefined,
                    background: isAnyFilterActive ? 'rgba(16, 185, 129, 0.12)' : undefined
                  }}
                  title={isAnyFilterActive ? `تصدير ${totalDoctors} موظف محددين إلى Excel` : 'تصدير إكسيل الدفعة كاملة'}
                >
                  <FileSpreadsheet size={14} color="#10B981" />
                  <span>{isAnyFilterActive ? `Excel المحدد (${totalDoctors})` : 'Excel'}</span>
                </a>

                <a
                  href={getExportUrl('pdf')}
                  download
                  className="btn-secondary"
                  style={{
                    textDecoration: 'none',
                    padding: '5px 10px',
                    fontSize: '0.8rem',
                    borderColor: isAnyFilterActive ? '#EF4444' : undefined,
                    background: isAnyFilterActive ? 'rgba(239, 68, 68, 0.12)' : undefined
                  }}
                  title={isAnyFilterActive ? `تصدير ${totalDoctors} موظف محددين إلى PDF` : 'تصدير PDF الدفعة كاملة'}
                >
                  <FileText size={14} color="#EF4444" />
                  <span>{isAnyFilterActive ? `PDF المحدد (${totalDoctors})` : 'PDF'}</span>
                </a>

                <button onClick={() => fetchDoctors()} className="btn-secondary" style={{ padding: '5px 10px', fontSize: '0.8rem' }}>
                  <RefreshCw size={14} />
                  <span>تحديث</span>
                </button>
              </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px 16px' }}>كود الموظف</th>
                    <th style={{ padding: '12px 16px' }}>اسم الموظف</th>
                    <th style={{ padding: '12px 16px' }}>الوظيفة / الصفة</th>
                    <th style={{ padding: '12px 16px' }}>القطاع والمكان</th>
                    <th style={{ padding: '12px 16px', textAlign: 'center' }}>أيام العمل</th>
                    <th style={{ padding: '12px 16px' }}>الوقت المقضي</th>
                    <th style={{ padding: '12px 16px' }}>وقت العجز</th>
                    <th style={{ padding: '12px 16px' }}>الوقت الإضافي</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    // Doctors Table Skeleton Loading
                    [1, 2, 3, 4, 5, 6].map((rowIdx) => (
                      <tr key={rowIdx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '14px 16px' }}><div className="skeleton" style={{ height: 16, width: 65 }} /></td>
                        <td style={{ padding: '14px 16px' }}><div className="skeleton" style={{ height: 16, width: 140 }} /></td>
                        <td style={{ padding: '14px 16px' }}><div className="skeleton" style={{ height: 14, width: 110 }} /></td>
                        <td style={{ padding: '14px 16px' }}><div className="skeleton" style={{ height: 14, width: 125 }} /></td>
                        <td style={{ padding: '14px 16px', textAlign: 'center' }}><div className="skeleton" style={{ height: 20, width: 45, margin: '0 auto' }} /></td>
                        <td style={{ padding: '14px 16px' }}><div className="skeleton" style={{ height: 16, width: 50 }} /></td>
                        <td style={{ padding: '14px 16px' }}><div className="skeleton" style={{ height: 20, width: 45 }} /></td>
                        <td style={{ padding: '14px 16px' }}><div className="skeleton" style={{ height: 20, width: 45 }} /></td>
                        <td style={{ padding: '14px 16px', textAlign: 'center' }}><div className="skeleton" style={{ height: 24, width: 75, margin: '0 auto' }} /></td>
                      </tr>
                    ))
                  ) : doctorsError ? (
                    // Doctors Table Error State
                    <tr>
                      <td colSpan={9} style={{ padding: '40px 20px', textAlign: 'center' }}>
                        <div style={{ maxWidth: 420, margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
                          <div style={{ width: 46, height: 46, borderRadius: 'var(--radius-full)', background: 'var(--danger-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f87171' }}>
                            <AlertCircle size={24} />
                          </div>
                          <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>فشل تحميل سجلات الموظفين</h4>
                          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{doctorsError}</p>
                          <button
                            onClick={() => fetchDoctors()}
                            className="btn-primary"
                            style={{ marginTop: 8, padding: '7px 16px', fontSize: '0.82rem' }}
                          >
                            <RefreshCw size={13} />
                            <span>إعادة المحاولة</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ) : doctors.length === 0 ? (
                    // Empty State
                    <tr>
                      <td colSpan={9} style={{ padding: '40px 20px', textAlign: 'center' }}>
                        {(search.trim() || selectedDept) ? (
                          <div style={{ maxWidth: 400, margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
                            <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-full)', background: 'rgba(59, 130, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-blue)' }}>
                              <Search size={20} />
                            </div>
                            <h4 style={{ fontSize: '0.95rem', fontWeight: 700 }}>لا توجد سجلات مطابقة لمعايير البحث</h4>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                              لم يتم العثور على أطباء أو موظفين يطابقون كلمة البحث {search ? `"${search}"` : ''} {selectedDept ? `في قسم (${selectedDept})` : ''}
                            </p>
                            <button
                              onClick={() => { setSearch(''); setSelectedDept(''); setPage(1); }}
                              className="btn-secondary"
                              style={{ marginTop: 6, padding: '6px 14px', fontSize: '0.8rem' }}
                            >
                              <X size={14} />
                              <span>إعادة تعيين والبحث في الكل</span>
                            </button>
                          </div>
                        ) : (
                          <div style={{ color: 'var(--text-muted)', padding: '20px' }}>
                            لا توجد سجلات محفوظة في هذه الدفعة حتى الآن.
                          </div>
                        )}
                      </td>
                    </tr>
                  ) : (
                    doctors.map((doc) => {
                      const isDocLoading = loadingDoctorDetail && activeDoctorCode === doc.emp_code;
                      return (
                        <tr
                          key={doc.emp_code}
                          className="glass-hover"
                          style={{ borderBottom: '1px solid var(--border-color)', cursor: isDocLoading ? 'wait' : 'pointer' }}
                          onClick={() => openDoctorModal(doc.emp_code)}
                        >
                          <td style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--accent-blue)' }}>
                            {doc.emp_code}
                          </td>
                          <td style={{ padding: '12px 16px', fontWeight: 600 }}>
                            {doc.emp_name}
                          </td>
                          <td style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                              <span>{doc.job_title}</span>
                              {doc.is_doctor && (
                                <span className="badge badge-mint" style={{ padding: '1px 6px', fontSize: '0.68rem', fontWeight: 600 }}>
                                  طبيب
                                </span>
                              )}
                            </div>
                          </td>
                          <td style={{ padding: '12px 16px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{doc.department}</div>
                            {doc.sector && doc.sector !== doc.department && (
                              <div style={{ fontSize: '0.72rem', color: 'var(--accent-blue)', marginTop: 2 }}>
                                {doc.sector}
                              </div>
                            )}
                          </td>
                          <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                            <span className="badge badge-blue">{doc.total_days_worked} يوم</span>
                          </td>
                          <td style={{ padding: '12px 16px', fontWeight: 600 }}>
                            {doc.total_time_spent}
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            {doc.total_deficit !== '0:00' ? (
                              <span className="badge badge-peach">{doc.total_deficit}</span>
                            ) : (
                              <span style={{ color: 'var(--text-muted)' }}>0:00</span>
                            )}
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            {doc.total_overtime !== '0:00' ? (
                              <span className="badge badge-mint">{doc.total_overtime}</span>
                            ) : (
                              <span style={{ color: 'var(--text-muted)' }}>0:00</span>
                            )}
                          </td>
                          <td style={{ padding: '12px 16px', textAlign: 'center' }} onClick={(e) => e.stopPropagation()}>
                            <div style={{ display: 'flex', gap: 6, justifyContent: 'center' }}>
                              <button
                                onClick={() => openDoctorModal(doc.emp_code)}
                                disabled={isDocLoading}
                                className="btn-secondary"
                                style={{ padding: '5px 8px', fontSize: '0.75rem' }}
                                title="عرض وتعديل كشف الطبيب"
                              >
                                {isDocLoading ? (
                                  <RefreshCw size={13} className="animate-spin" />
                                ) : (
                                  <Edit3 size={13} />
                                )}
                                <span>{isDocLoading ? 'جاري الفتح...' : 'تعديل'}</span>
                              </button>
                              <a
                                href={`/api/export/pdf?batch_id=${activeBatchId}&doctor_code=${doc.emp_code}`}
                                download
                                className="btn-secondary"
                                style={{ padding: '5px 8px', textDecoration: 'none' }}
                                title="تصدير كشف الطبيب PDF"
                              >
                                <FileText size={13} color="#EF4444" />
                              </a>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalDoctors > 0 && (
              <div style={{
                padding: '12px 20px',
                borderTop: '1px solid var(--border-color)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: 12,
                fontSize: '0.85rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)' }}>
                  <span>
                    عرض السجلات {Math.min((page - 1) * pageSize + 1, totalDoctors)} إلى {Math.min(page * pageSize, totalDoctors)} من أصل {totalDoctors}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span>عدد السجلات:</span>
                    <select
                      value={pageSize}
                      onChange={(e) => {
                        const newSize = Number(e.target.value);
                        setPageSize(newSize);
                        setPage(1);
                      }}
                      style={{
                        padding: '4px 8px',
                        borderRadius: 'var(--radius-sm)',
                        background: 'var(--bg-primary)',
                        border: '1px solid var(--border-color)',
                        color: 'var(--text-primary)',
                        fontSize: '0.8rem'
                      }}
                    >
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                      <option value={200}>200</option>
                    </select>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <button
                    onClick={() => setPage((p) => Math.max(p - 1, 1))}
                    disabled={page <= 1}
                    className="btn-secondary"
                    style={{ padding: '6px 14px', fontSize: '0.8rem', opacity: page <= 1 ? 0.4 : 1, cursor: page <= 1 ? 'not-allowed' : 'pointer' }}
                  >
                    الصفحة السابقة
                  </button>
                  <span style={{ fontWeight: 700, color: 'var(--accent-blue)', padding: '0 4px' }}>
                    {page} / {Math.max(Math.ceil(totalDoctors / pageSize), 1)}
                  </span>
                  <button
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page >= Math.ceil(totalDoctors / pageSize)}
                    className="btn-secondary"
                    style={{ padding: '6px 14px', fontSize: '0.8rem', opacity: page >= Math.ceil(totalDoctors / pageSize) ? 0.4 : 1, cursor: page >= Math.ceil(totalDoctors / pageSize) ? 'not-allowed' : 'pointer' }}
                  >
                    الصفحة التالية
                  </button>
                </div>
              </div>
            )}
          </section>
          {/* Footer Attribution */}
          <footer style={{
            marginTop: 'auto',
            paddingTop: 24,
            paddingBottom: 10,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '0.82rem',
            color: 'var(--text-muted)',
            borderTop: '1px solid var(--border-color)',
            flexWrap: 'wrap',
            gap: 12
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#10B981' }} />
              <span>إدارة نظم المعلومات والتحول الرقمي - شركة الخدمات الطبية</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)' }}>
              <span>Created with ❤️ by <strong style={{ color: 'var(--accent-blue)', fontWeight: 700 }}>Eng. Mohamed Marei</strong></span>
            </div>
          </footer>

        </main>

      </div>

      {/* 3. DOCTOR DETAIL & IN-PLACE EDITING MODAL */}
      {selectedDoctor && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 50,
          padding: 20
        }}>
          <div className="glass animate-fade-in" style={{
            background: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-lg)',
            width: '100%',
            maxWidth: 1100,
            maxHeight: '92vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: 'var(--shadow-lg)'
          }}>

            {/* Modal Header */}
            <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>
                    كشف بصمات: {selectedDoctor.emp_name}
                  </h3>
                  <span className="badge badge-blue">كود: {selectedDoctor.emp_code}</span>
                  {saveSuccess && <span className="badge badge-mint">تم حفظ التعديلات بنجاح!</span>}
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  الوظيفة: {selectedDoctor.job_title} | الإدارة: {selectedDoctor.department} | العقد: {selectedDoctor.contract}
                </p>
              </div>

              <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                {/* Mode Toggle Button */}
                <button
                  onClick={() => setIsEditMode(!isEditMode)}
                  className={isEditMode ? 'btn-secondary' : 'btn-primary'}
                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                >
                  <Edit3 size={14} />
                  <span>{isEditMode ? 'إلغاء وضع التعديل' : 'تفعيل وضع التعديل اليدوي'}</span>
                </button>

                {isEditMode && (
                  <button
                    onClick={handleSaveEdits}
                    disabled={savingEdit}
                    className="btn-primary"
                    style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)', padding: '6px 14px', fontSize: '0.8rem' }}
                  >
                    {savingEdit ? <RefreshCw size={14} className="animate-spin" /> : <Save size={14} />}
                    <span>{savingEdit ? 'جاري الحفظ...' : 'حفظ التعديلات'}</span>
                  </button>
                )}

                <a
                  href={getApiUrl(`/api/export/pdf?batch_id=${activeBatchId}&doctor_code=${selectedDoctor.emp_code}`)}
                  download
                  className="btn-secondary"
                  style={{ textDecoration: 'none', padding: '6px 10px', display: 'inline-flex', alignItems: 'center', gap: 4 }}
                  title="تصدير كشف الموظف PDF"
                >
                  <Download size={14} />
                  <span>PDF</span>
                </a>

                <a
                  href={getApiUrl(`/api/export/excel?batch_id=${activeBatchId}&doctor_code=${selectedDoctor.emp_code}`)}
                  download
                  className="btn-secondary"
                  style={{ textDecoration: 'none', padding: '6px 10px', display: 'inline-flex', alignItems: 'center', gap: 4 }}
                  title="تصدير كشف الموظف Excel"
                >
                  <Download size={14} />
                  <span>Excel</span>
                </a>

                <button onClick={() => setSelectedDoctor(null)} className="btn-secondary" style={{ padding: '6px 8px' }}>
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Attendance Table Body */}
            <div style={{ padding: 20, overflowY: 'auto' }}>

              {isEditMode && (
                <div style={{ padding: '10px 14px', borderRadius: 'var(--radius-sm)', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', marginBottom: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                  <span>💡 أنت الآن في <strong>وضع التعديل اليدوي</strong>: يمكنك تعديل أوقات الحضور والانصراف، تغيير الشفت، ضبط العجز، أو إضافة أيام عمل مفقودة.</span>
                  <button onClick={handleAddDayRow} className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
                    <Plus size={13} />
                    <span>إضافة يوم جديد</span>
                  </button>
                </div>
              )}

              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center', fontSize: '0.8rem', border: '1px solid var(--border-color)' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-primary)', borderBottom: '2px solid var(--border-color)' }}>
                    <th style={{ padding: '8px 10px' }}>التاريخ</th>
                    <th style={{ padding: '8px 10px' }}>اليوم</th>
                    <th style={{ padding: '8px 10px' }}>حضور</th>
                    <th style={{ padding: '8px 10px' }}>انصراف</th>
                    <th style={{ padding: '8px 10px' }}>حضور مسائي</th>
                    <th style={{ padding: '8px 10px' }}>انصراف مسائي</th>
                    <th style={{ padding: '8px 10px' }}>الوقت المقضي</th>
                    <th style={{ padding: '8px 10px' }}>نوع الشفت</th>
                    <th style={{ padding: '8px 10px' }}>وقت التأخير</th>
                    <th style={{ padding: '8px 10px' }}>الوقت الإضافي</th>
                    <th style={{ padding: '8px 6px', fontSize: '0.72rem' }}>مفتاح الحضور (الإجراء)</th>
                    <th style={{ padding: '8px 6px', fontSize: '0.72rem' }}>مفتاح الانصراف (الإجراء)</th>
                    <th style={{ padding: '8px 6px', fontSize: '0.72rem' }}>نوع التحقق (البصمة)</th>
                    <th style={{ padding: '8px 6px', fontSize: '0.72rem' }}>جهاز البصمة</th>
                    {isEditMode && <th style={{ padding: '8px 10px' }}>إجراء</th>}
                  </tr>
                </thead>
                <tbody>
                  {(isEditMode ? editedRecords : selectedDoctor.records).map((r, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>

                      {/* Date */}
                      <td style={{ padding: '8px' }}>
                        {isEditMode ? (
                          <input
                            type="date"
                            value={r.date}
                            onChange={(e) => handleRecordChange(idx, 'date', e.target.value)}
                            style={{ padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.8rem' }}
                          />
                        ) : (
                          <strong>{r.date}</strong>
                        )}
                      </td>

                      {/* Day Name */}
                      <td style={{ padding: '8px' }}>
                        {isEditMode ? (
                          <input
                            type="text"
                            value={r.day}
                            onChange={(e) => handleRecordChange(idx, 'day', e.target.value)}
                            style={{ width: 70, textAlign: 'center', padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.8rem' }}
                          />
                        ) : (
                          r.day
                        )}
                      </td>


                      {/* Check-in 1 */}
                      <td style={{ padding: '8px', background: !isEditMode && r.is_late_arrival ? 'var(--peach-bg)' : undefined }}>
                        {isEditMode ? (
                          <input
                            type="text"
                            value={r.check_in_1}
                            placeholder="8:30 AM"
                            onChange={(e) => handleRecordChange(idx, 'check_in_1', e.target.value)}
                            style={{ width: 85, textAlign: 'center', padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.8rem' }}
                          />
                        ) : (
                          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 4, flexWrap: 'wrap' }}>
                            {r.check_in_1 ? (
                              <span style={{ fontWeight: 600 }}>{r.check_in_1}</span>
                            ) : (r.key_warning === 'end_of_24h' || (!r.check_in_1 && r.check_out_1 && ['24H', '24+A', '24+A+B'].includes(r.shift_type))) ? (
                              <span style={{
                                background: 'rgba(99, 102, 241, 0.12)',
                                color: '#818cf8',
                                border: '1px solid rgba(99, 102, 241, 0.3)',
                                borderRadius: 5,
                                padding: '2px 6px',
                                fontSize: '0.68rem',
                                fontWeight: 700,
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: 2
                              }} title="استكمال النوبتجية الممتدة من اليوم السابق">
                                ↘️ استكمال نوبتجية
                              </span>
                            ) : (
                              <span style={{ color: 'var(--text-muted, #94a3b8)' }}>-</span>
                            )}
                            {r.is_late_arrival && (
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (selectedDoctor) {
                                    setSelectedAlertRecord({
                                      record: r,
                                      docName: selectedDoctor.emp_name,
                                      empCode: selectedDoctor.emp_code
                                    });
                                  }
                                }}
                                title="تأخير في الحضور (بعد 08:45 ص) - اضغط لعرض التفاصيل"
                                style={{
                                  background: 'rgba(239, 68, 68, 0.15)',
                                  border: '1px solid rgba(239, 68, 68, 0.4)',
                                  color: '#ef4444',
                                  borderRadius: 4,
                                  padding: '1px 5px',
                                  fontSize: '0.65rem',
                                  fontWeight: 700,
                                  cursor: 'pointer'
                                }}
                              >
                                تأخير
                              </button>
                            )}
                          </div>
                        )}
                      </td>

                      {/* Check-out 1 */}
                      <td style={{ padding: '8px' }}>
                        {isEditMode ? (
                          <input
                            type="text"
                            value={r.check_out_1}
                            placeholder="2:30 PM"
                            onChange={(e) => handleRecordChange(idx, 'check_out_1', e.target.value)}
                            style={{ width: 85, textAlign: 'center', padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.8rem' }}
                          />
                        ) : (
                          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 4, flexWrap: 'wrap' }}>
                            {r.check_out_1 ? (
                              <span style={{ fontWeight: 600 }}>{r.check_out_1}</span>
                            ) : (r.key_warning === 'start_of_24h' || (r.check_in_1 && !r.check_out_1 && r.key_warning === 'start_of_24h')) ? (
                              <span style={{
                                background: 'rgba(59, 130, 246, 0.12)',
                                color: '#60a5fa',
                                border: '1px solid rgba(59, 130, 246, 0.3)',
                                borderRadius: 5,
                                padding: '2px 6px',
                                fontSize: '0.68rem',
                                fontWeight: 700,
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: 2
                              }} title="مستمر حتى تاريخ الخروج غداً صباحاً">
                                ↗️ الخروج غداً
                              </span>
                            ) : (
                              <span style={{ color: 'var(--text-muted, #94a3b8)' }}>-</span>
                            )}
                          </div>
                        )}
                      </td>

                      {/* Check-in 2 */}
                      <td style={{ padding: '8px' }}>
                        {isEditMode ? (
                          <input
                            type="text"
                            value={r.check_in_2}
                            placeholder="8:30 PM"
                            onChange={(e) => handleRecordChange(idx, 'check_in_2', e.target.value)}
                            style={{ width: 85, textAlign: 'center', padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.8rem' }}
                          />
                        ) : (
                          <span style={{ color: r.check_in_2 ? 'var(--text-primary)' : 'var(--text-muted, #94a3b8)', fontWeight: r.check_in_2 ? 600 : 400 }}>
                            {r.check_in_2 || '-'}
                          </span>
                        )}
                      </td>

                      {/* Check-out 2 */}
                      <td style={{ padding: '8px' }}>
                        {isEditMode ? (
                          <input
                            type="text"
                            value={r.check_out_2}
                            placeholder="8:30 AM"
                            onChange={(e) => handleRecordChange(idx, 'check_out_2', e.target.value)}
                            style={{ width: 85, textAlign: 'center', padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.8rem' }}
                          />
                        ) : (
                          <span style={{ color: r.check_out_2 ? 'var(--text-primary)' : 'var(--text-muted, #94a3b8)', fontWeight: r.check_out_2 ? 600 : 400 }}>
                            {r.check_out_2 || '-'}
                          </span>
                        )}
                      </td>

                      {/* Time Spent */}
                      <td style={{ padding: '8px', fontWeight: 700, background: !isEditMode && r.is_deficit ? 'var(--peach-bg)' : undefined, color: !isEditMode && r.is_deficit ? 'var(--peach-text)' : undefined }}>
                        {isEditMode ? (
                          <input
                            type="text"
                            value={r.time_spent}
                            placeholder="6:00"
                            onChange={(e) => handleRecordChange(idx, 'time_spent', e.target.value)}
                            style={{ width: 65, textAlign: 'center', padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontWeight: 700, fontSize: '0.8rem' }}
                          />
                        ) : (
                          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 3, justifyContent: 'center' }}>
                            {r.time_spent && r.time_spent !== '0:00' && <span style={{ fontSize: '0.75rem', opacity: 0.8 }}>⏱️</span>}
                            <span>{r.time_spent || '0:00'}</span>
                          </div>
                        )}
                      </td>

                      {/* Shift Type */}
                      <td style={{ padding: '8px', fontWeight: 700 }}>
                        {isEditMode ? (
                          <select
                            value={r.shift_type}
                            onChange={(e) => handleRecordChange(idx, 'shift_type', e.target.value)}
                            style={{ padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontWeight: 700, fontSize: '0.8rem' }}
                          >
                            <option value="">(فارغ - بصمة مفردة)</option>
                            <option value="A">A (صباحي 6س)</option>
                            <option value="B">B (مسائي 6س)</option>
                            <option value="L">L (طويل 12س)</option>
                            <option value="C">C (سهر 12س)</option>
                            <option value="BC">BC (مسائي+سهر 18س)</option>
                            <option value="CA">CA (سهر+صباحي 18س)</option>
                            <option value="24H">24H (نوبتجية كاملة 24س)</option>
                            <option value="24+A">24+A (نوبتجية + صباحي 30س)</option>
                            <option value="24+A+B">24+A+B (نوبتجية + صباحي + مسائي 36س)</option>
                            <option value="غير محدد">غير محدد</option>
                          </select>
                        ) : (
                          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                            {(() => {
                              if (!r.shift_type) {
                                if (r.key_warning === 'start_of_24h') {
                                  return (
                                    <span style={{
                                      display: 'inline-flex',
                                      alignItems: 'center',
                                      gap: 3,
                                      padding: '3px 8px',
                                      borderRadius: 6,
                                      background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.15))',
                                      border: '1px solid rgba(99, 102, 241, 0.35)',
                                      color: '#a5b4fc',
                                      fontSize: '0.72rem',
                                      fontWeight: 800
                                    }}>
                                      🌙 بداية نوبتجية
                                    </span>
                                  );
                                }
                                return <span style={{ color: 'var(--text-muted, #94a3b8)' }}>-</span>;
                              }

                              const badgeConfig: Record<string, { bg: string; border: string; color: string; label: string }> = {
                                '24+A': {
                                  bg: 'linear-gradient(135deg, rgba(168, 85, 247, 0.22), rgba(236, 72, 153, 0.22))',
                                  border: 'rgba(168, 85, 247, 0.5)',
                                  color: '#d8b4fe',
                                  label: '🌟 24+A (30س)'
                                },
                                '24H': {
                                  bg: 'linear-gradient(135deg, rgba(14, 165, 233, 0.2), rgba(59, 130, 246, 0.2))',
                                  border: 'rgba(14, 165, 233, 0.5)',
                                  color: '#7dd3fc',
                                  label: '⏱️ 24H (24س)'
                                },
                                '24+A+B': {
                                  bg: 'linear-gradient(135deg, rgba(234, 179, 8, 0.22), rgba(249, 115, 22, 0.22))',
                                  border: 'rgba(234, 179, 8, 0.5)',
                                  color: '#fde047',
                                  label: '👑 24+A+B (36س)'
                                },
                                'A': {
                                  bg: 'rgba(59, 130, 246, 0.14)',
                                  border: 'rgba(59, 130, 246, 0.35)',
                                  color: '#93c5fd',
                                  label: 'A (صباحي 6س)'
                                },
                                'B': {
                                  bg: 'rgba(16, 185, 129, 0.14)',
                                  border: 'rgba(16, 185, 129, 0.35)',
                                  color: '#6ee7b7',
                                  label: 'B (مسائي 6س)'
                                },
                                'L': {
                                  bg: 'rgba(139, 92, 246, 0.14)',
                                  border: 'rgba(139, 92, 246, 0.35)',
                                  color: '#c4b5fd',
                                  label: 'L (طويل 12س)'
                                },
                                'C': {
                                  bg: 'rgba(236, 72, 153, 0.14)',
                                  border: 'rgba(236, 72, 153, 0.35)',
                                  color: '#f472b6',
                                  label: 'C (سهر 12س)'
                                },
                                'BC': {
                                  bg: 'rgba(20, 184, 166, 0.14)',
                                  border: 'rgba(20, 184, 166, 0.35)',
                                  color: '#5eead4',
                                  label: 'BC (مركب 18س)'
                                },
                                'CA': {
                                  bg: 'rgba(244, 63, 94, 0.14)',
                                  border: 'rgba(244, 63, 94, 0.35)',
                                  color: '#fda4af',
                                  label: 'CA (مركب 18س)'
                                }
                              };

                              const cfg = badgeConfig[r.shift_type] || {
                                bg: 'rgba(148, 163, 184, 0.14)',
                                border: 'rgba(148, 163, 184, 0.3)',
                                color: 'var(--text-primary)',
                                label: r.shift_type
                              };

                              return (
                                <span style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  padding: '2px 8px',
                                  borderRadius: 6,
                                  background: cfg.bg,
                                  border: `1px solid ${cfg.border}`,
                                  color: cfg.color,
                                  fontSize: '0.74rem',
                                  fontWeight: 800,
                                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                                }}>
                                  {cfg.label}
                                </span>
                              );
                            })()}

                            {r.key_warning && (
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (selectedDoctor) {
                                    setSelectedAlertRecord({
                                      record: r,
                                      docName: selectedDoctor.emp_name,
                                      empCode: selectedDoctor.emp_code
                                    });
                                  }
                                }}
                                title="اضغط لعرض تفاصيل تنبيه البصمة والمطابقة الذكية"
                                style={{
                                  cursor: 'pointer',
                                  background: 'rgba(245, 158, 11, 0.15)',
                                  border: '1px solid rgba(245, 158, 11, 0.45)',
                                  color: '#d97706',
                                  borderRadius: 5,
                                  padding: '2px 6px',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: 3,
                                  fontSize: '0.72rem',
                                  fontWeight: 800
                                }}
                              >
                                ⚠️ تفاصيل
                              </button>
                            )}
                          </div>
                        )}
                      </td>

                      {/* Deficit Time */}
                      <td style={{ padding: '8px', fontWeight: 700, background: !isEditMode && r.is_deficit ? 'var(--peach-bg)' : undefined, color: !isEditMode && r.is_deficit ? 'var(--peach-text)' : undefined }}>
                        {isEditMode ? (
                          <input
                            type="text"
                            value={r.deficit_time}
                            placeholder="0:00"
                            onChange={(e) => handleRecordChange(idx, 'deficit_time', e.target.value)}
                            style={{ width: 65, textAlign: 'center', padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--peach-text)', fontWeight: 700, fontSize: '0.8rem' }}
                          />
                        ) : (
                          <span style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 3,
                            padding: r.is_deficit ? '2px 7px' : '0',
                            borderRadius: 5,
                            background: r.is_deficit ? 'rgba(239, 68, 68, 0.12)' : 'transparent',
                            color: r.is_deficit ? '#ef4444' : 'var(--text-muted, #94a3b8)',
                            fontWeight: r.is_deficit ? 800 : 400
                          }}>
                            {r.is_deficit && '⚠️'} {r.deficit_time || '0:00'}
                          </span>
                        )}
                      </td>

                      {/* Overtime Time */}
                      <td style={{ padding: '8px', fontWeight: 700, background: !isEditMode && r.is_overtime ? 'var(--mint-bg)' : undefined, color: !isEditMode && r.is_overtime ? 'var(--mint-text)' : undefined }}>
                        {isEditMode ? (
                          <input
                            type="text"
                            value={r.overtime_time}
                            placeholder="0:00"
                            onChange={(e) => handleRecordChange(idx, 'overtime_time', e.target.value)}
                            style={{ width: 65, textAlign: 'center', padding: '4px', borderRadius: 4, background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--mint-text)', fontWeight: 700, fontSize: '0.8rem' }}
                          />
                        ) : (
                          <span style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 2,
                            padding: r.is_overtime ? '2px 7px' : '0',
                            borderRadius: 5,
                            background: r.is_overtime ? 'rgba(16, 185, 129, 0.12)' : 'transparent',
                            color: r.is_overtime ? '#10b981' : 'var(--text-muted, #94a3b8)',
                            fontWeight: r.is_overtime ? 800 : 400
                          }}>
                            {r.is_overtime && '+'} {r.overtime_time || '0:00'}
                          </span>
                        )}
                      </td>

                      {/* Function Key - In (Action) */}
                      <td style={{ padding: '6px 4px', fontSize: '0.72rem' }}>
                        {(() => {
                          const renderInBadge = (k: string) => {
                            if (!k) return null;
                            const action = k === 'F1' ? 'حضور' : k === 'F3' ? 'حضور مسائي' : k === 'F2' ? 'انصراف' : k === 'F4' ? 'انصراف مسائي' : k;
                            const isWrong = ['F2', 'F4'].includes(k);
                            const bg = isWrong ? 'rgba(239, 68, 68, 0.15)' : k === 'F1' ? 'rgba(59, 130, 246, 0.12)' : 'rgba(139, 92, 246, 0.12)';
                            const color = isWrong ? '#ef4444' : k === 'F1' ? '#3b82f6' : '#8b5cf6';
                            return (
                              <span
                                onClick={() => {
                                  if (selectedDoctor && (isWrong || r.key_warning)) {
                                    setSelectedAlertRecord({
                                      record: r,
                                      docName: selectedDoctor.emp_name,
                                      empCode: selectedDoctor.emp_code
                                    });
                                  }
                                }}
                                title={`مفتاح: ${k} | الإجراء: ${action}${isWrong ? ' (خطأ: تم استخدام مفتاح خروج للدخول - اضغط للتفاصيل)' : ''}`}
                                style={{ display: 'inline-flex', alignItems: 'center', gap: 3, padding: '2px 6px', borderRadius: 4, background: bg, color: color, fontWeight: 700, fontSize: '0.68rem', border: `1px solid ${color}33`, whiteSpace: 'nowrap', cursor: (isWrong || r.key_warning) ? 'pointer' : 'default' }}
                              >
                                {isWrong && '⚠️ '}{k} ({action})
                              </span>
                            );
                          };
                          return (
                            <>
                              {renderInBadge(r.in_1_key || '')}
                              {r.in_2_key && <><br/>{renderInBadge(r.in_2_key)}</>}
                            </>
                          );
                        })()}
                      </td>

                      {/* Function Key - Out (Action) */}
                      <td style={{ padding: '6px 4px', fontSize: '0.72rem' }}>
                        {(() => {
                          const renderOutBadge = (k: string, inK: string) => {
                            if (!k) return null;
                            const action = k === 'F2' ? 'انصراف' : k === 'F4' ? 'انصراف مسائي' : k === 'F1' ? 'حضور' : k === 'F3' ? 'حضور مسائي' : k;
                            const isWrong = ['F1', 'F3'].includes(k);
                            const isRepeat = inK && k === inK;
                            const hasWarn = isWrong || isRepeat;
                            const bg = hasWarn ? 'rgba(245, 158, 11, 0.15)' : k === 'F2' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(236, 72, 153, 0.12)';
                            const color = hasWarn ? '#d97706' : k === 'F2' ? '#10b981' : '#ec4899';
                            return (
                              <span
                                onClick={() => {
                                  if (selectedDoctor && (hasWarn || r.key_warning)) {
                                    setSelectedAlertRecord({
                                      record: r,
                                      docName: selectedDoctor.emp_name,
                                      empCode: selectedDoctor.emp_code
                                    });
                                  }
                                }}
                                title={`مفتاح: ${k} | الإجراء: ${action}${isRepeat ? ' (خطأ: تكرار نفس مفتاح الدخول - اضغط للتفاصيل)' : isWrong ? ' (خطأ: تم استخدام مفتاح حضور للانصراف - اضغط للتفاصيل)' : ''}`}
                                style={{ display: 'inline-flex', alignItems: 'center', gap: 3, padding: '2px 6px', borderRadius: 4, background: bg, color: color, fontWeight: 700, fontSize: '0.68rem', border: `1px solid ${color}33`, whiteSpace: 'nowrap', cursor: (hasWarn || r.key_warning) ? 'pointer' : 'default' }}
                              >
                                {hasWarn && '⚠️ '}{k} ({action})
                              </span>
                            );
                          };
                          return (
                            <>
                              {renderOutBadge(r.out_1_key || '', r.in_1_key || '')}
                              {r.out_2_key && <><br/>{renderOutBadge(r.out_2_key, r.in_2_key || '')}</>}
                            </>
                          );
                        })()}
                      </td>

                      {/* Auth Type / Fingerprint Method */}
                      <td style={{ padding: '6px 4px', fontSize: '0.7rem' }}>
                        {(() => {
                          const a1 = r.in_1_auth_type || '';
                          const a2 = r.out_1_auth_type || '';
                          const formatAuth = (a: string) => {
                            if (!a) return null;
                            const isFinger = a.toLowerCase().includes('finger');
                            const isFace = a.toLowerCase().includes('face');
                            const isPass = a.toLowerCase().includes('password');
                            const icon = isFace ? '👤' : isFinger ? '👆' : isPass ? '🔑' : '📱';
                            const label = isFace ? 'بصمة وجه' : isFinger ? 'بصمة إصبع' : isPass ? 'رمز سري' : a;
                            const bg = isFinger ? 'rgba(16, 185, 129, 0.12)' : isFace ? 'rgba(59, 130, 246, 0.1)' : 'rgba(156, 163, 175, 0.1)';
                            const color = isFinger ? '#10b981' : isFace ? '#3b82f6' : 'inherit';
                            return (
                              <span
                                title={`طريقة التحقق: ${a}`}
                                style={{ display: 'inline-flex', alignItems: 'center', gap: 3, padding: '2px 5px', borderRadius: 4, background: bg, color: color, fontWeight: isFinger ? 700 : 500, fontSize: '0.68rem', whiteSpace: 'nowrap' }}
                              >
                                {icon} {label}
                              </span>
                            );
                          };
                          return (
                            <>
                              {formatAuth(a1)}
                              {a2 && a1 !== a2 && <><br/>{formatAuth(a2)}</>}
                            </>
                          );
                        })()}
                      </td>

                      {/* Terminal Name */}
                      <td style={{ padding: '6px 4px', fontSize: '0.65rem', maxWidth: 110, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {(() => {
                          const t1 = r.in_1_terminal || '';
                          const t2 = r.out_1_terminal || '';
                          const display = t1 || t2;
                          const both = t1 && t2 && t1 !== t2;
                          return (
                            <>
                              {display && (
                                <span
                                  title={both ? `جهاز الحضور: ${t1}\nجهاز الانصراف: ${t2}` : `جهاز البصمة: ${display}`}
                                  style={{ cursor: 'help', display: 'inline-block', padding: '1px 4px', borderRadius: 3, background: 'rgba(100, 116, 139, 0.08)' }}
                                >
                                  🖥️ {display}
                                </span>
                              )}
                              {both && (
                                <><br/><span title={`جهاز الانصراف: ${t2}`} style={{ opacity: 0.75, fontSize: '0.62rem' }}>↔ {t2}</span></>
                              )}
                            </>
                          );
                        })()}
                      </td>

                      {/* Delete button in edit mode */}
                      {isEditMode && (
                        <td style={{ padding: '8px' }}>
                          <button
                            onClick={() => handleDeleteDayRow(idx)}
                            style={{ background: 'none', border: 'none', color: '#F87171', cursor: 'pointer', padding: 4 }}
                            title="حذف هذا اليوم"
                          >
                            <Trash2 size={14} />
                          </button>
                        </td>
                      )}

                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Doctor Summary in Modal */}
              <div style={{ marginTop: 18, padding: 14, borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
                <div>
                  <strong>إجمالي أيام العمل: </strong>{selectedDoctor.total_days_worked} يوم
                </div>
                <div>
                  <strong>إجمالي الوقت المقضي: </strong>{selectedDoctor.total_time_spent} س
                </div>
                <div style={{ color: 'var(--peach-text)' }}>
                  <strong>إجمالي العجز / التأخير: </strong>{selectedDoctor.total_deficit} س
                </div>
                <div style={{ color: 'var(--mint-text)' }}>
                  <strong>إجمالي الوقت الإضافي: </strong>{selectedDoctor.total_overtime} س
                </div>
              </div>

            </div>

          </div>
        </div>
      )}

      {/* 4. MODAL: IMPORT NEW BATCH */}
      {showNewBatchModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 50,
          padding: 20
        }}>
          <div className="glass animate-fade-in" style={{
            background: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-lg)',
            width: '100%',
            maxWidth: 580,
            padding: 26,
            boxShadow: 'var(--shadow-lg)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>استيراد دفعة بصمات جديدة</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  سيتم حفظها وأرشفتها كدفعة مستقلة بتاريخ ووقت الإنشاء
                </p>
              </div>
              <button onClick={() => setShowNewBatchModal(false)} className="btn-secondary" style={{ padding: '6px 8px' }}>
                <X size={16} />
              </button>
            </div>

            <div style={{
              background: 'rgba(59, 130, 246, 0.08)',
              border: '1px solid rgba(59, 130, 246, 0.25)',
              borderRadius: 'var(--radius-md)',
              padding: '10px 14px',
              marginBottom: 16,
              fontSize: '0.82rem',
              color: 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}>
              <Sparkles size={16} color="var(--primary-color)" />
              <span>
                <strong>خيار افتراضي مرن:</strong> يمكنك ترك ملفات البصمة فارغة للاعتماد على الملفات الافتراضية للسيستم (4 ملفات AuthLogList) أو رفع ملفات أسبوع/شهر جديد.
              </span>
            </div>

            <form onSubmit={handleNewBatchSubmit}>
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 6 }}>
                  اسم أو عنوان الدفعة:
                </label>
                <input
                  type="text"
                  placeholder="مثال: أسبوع 19 إلى 25 أكتوبر 2026 (أو اتركه فارغاً للتسمية التلقائية)"
                  value={newBatchName}
                  onChange={(e) => setNewBatchName(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontFamily: 'var(--font-main)' }}
                />
              </div>

              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', fontWeight: 600, marginBottom: 6 }}>
                  <span>ملفات قاعدة بيانات الموظفين (XLSX) - يمكن اختيار ملف أو أكثر:</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 500, color: (newMasterFiles && newMasterFiles.length > 0) ? 'var(--accent-mint)' : 'var(--text-muted)' }}>
                    {(newMasterFiles && newMasterFiles.length > 0)
                      ? `✓ تم اختيار: ${newMasterFiles.length} ملف`
                      : '(اختياري - افتراضي)'}
                  </span>
                </label>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  multiple
                  onChange={(e) => setNewMasterFiles(e.target.files)}
                  style={{ width: '100%', padding: '9px', borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
                />
              </div>

              <div style={{ marginBottom: 18 }}>
                <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', fontWeight: 600, marginBottom: 6 }}>
                  <span>ملفات سجلات البصمة للدفعة (AuthLogList_*.xlsx):</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 500, color: (newAuthFiles && newAuthFiles.length > 0) ? 'var(--accent-mint)' : '#38bdf8' }}>
                    {(newAuthFiles && newAuthFiles.length > 0)
                      ? `✓ تم تحديد ${newAuthFiles.length} ملف`
                      : '⚡ سيتم استخدام الـ 4 ملفات الافتراضية'}
                  </span>
                </label>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  multiple
                  onChange={(e) => setNewAuthFiles(e.target.files)}
                  style={{ width: '100%', padding: '9px', borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
                />
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                  {(!newAuthFiles || newAuthFiles.length === 0) ? (
                    <span style={{ color: '#38bdf8' }}>💡 لم يتم اختيار ملفات — سيتم استخدام ملفات البصمة الأصلية في النظام تلقائياً.</span>
                  ) : (
                    <span>📁 سيتم استيراد وحفظ {newAuthFiles.length} ملف بصمة محدد في الدفعة الجديدة.</span>
                  )}
                </p>
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6 }}>
                  ملاحظات اختيارية:
                </label>
                <input
                  type="text"
                  placeholder="أي ملاحظات إضافية..."
                  value={newBatchNotes}
                  onChange={(e) => setNewBatchNotes(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.85rem' }}
                />
              </div>

              <button
                type="submit"
                disabled={uploadingNew}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center', padding: '11px' }}
              >
                {uploadingNew ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    <span>جاري المعالجة والأرشفة...</span>
                  </>
                ) : (
                  <>
                    <Upload size={16} />
                    <span>حفظ الدفعة الجديدة</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* 5. MODAL: APPEND FILES TO ACTIVE BATCH */}
      {showAppendModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 50,
          padding: 20
        }}>
          <div className="glass animate-fade-in" style={{
            background: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-lg)',
            width: '100%',
            maxWidth: 560,
            padding: 26,
            boxShadow: 'var(--shadow-lg)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>إضافة ملفات للدفعة الحالية</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  إلحاق ماكينات بصمة إضافية (مثل MSC-F1) أو ملف موظفين محدث بالدفعة: <strong>{activeBatch?.name}</strong>
                </p>
              </div>
              <button onClick={() => setShowAppendModal(false)} className="btn-secondary" style={{ padding: '6px 8px' }}>
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleAppendFilesSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 6 }}>
                  ملفات البصمة الإضافية (AuthLogList_*.xlsx):
                </label>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  multiple
                  onChange={(e) => setAppendAuthFiles(e.target.files)}
                  required
                  style={{ width: '100%', padding: '9px', borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
                />
              </div>

              <div style={{ marginBottom: 22 }}>
                <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 6 }}>
                  <span>ملفات موظفين بديلة/محدثة (اختياري):</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 500, color: (appendMasterFiles && appendMasterFiles.length > 0) ? 'var(--accent-mint)' : 'var(--text-muted)' }}>
                    {(appendMasterFiles && appendMasterFiles.length > 0) ? `✓ تم اختيار: ${appendMasterFiles.length} ملف` : ''}
                  </span>
                </label>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  multiple
                  onChange={(e) => setAppendMasterFiles(e.target.files)}
                  style={{ width: '100%', padding: '9px', borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
                />
              </div>

              <button
                type="submit"
                disabled={appending}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center', padding: '11px' }}
              >
                {appending ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    <span>جاري دمج الملفات وإعادة الاحتساب...</span>
                  </>
                ) : (
                  <>
                    <FilePlus2 size={16} />
                    <span>دمج الملفات وإعادة احتساب الدفعة</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* 5.5 BIOMETRIC ALERT DETAILS MODAL */}
      {selectedAlertRecord && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.65)',
          backdropFilter: 'blur(5px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 70,
          padding: 20
        }}>
          <div className="glass animate-fade-in" style={{
            background: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-lg)',
            width: '100%',
            maxWidth: 620,
            padding: 24,
            boxShadow: 'var(--shadow-lg)',
            border: '1px solid var(--border-color)',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, borderBottom: '1px solid var(--border-color)', paddingBottom: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 38, height: 38, borderRadius: '50%', background: 'rgba(245, 158, 11, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#d97706' }}>
                  <AlertTriangle size={22} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0 }}>
                    تفاصيل تنبيه البصمة والمطابقة الذكية
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
                    {selectedAlertRecord.docName} (كود: {selectedAlertRecord.empCode}) | {selectedAlertRecord.record.day} {selectedAlertRecord.record.date}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedAlertRecord(null)}
                className="btn-secondary"
                style={{ padding: '6px 8px' }}
              >
                <X size={16} />
              </button>
            </div>

            {/* Alert Classification & Human Explanation Card */}
            {(() => {
              const r = selectedAlertRecord.record;
              const kw = r.key_warning;
              let alertTitle = "تنبيه في حركة البصمة";
              let alertDesc = "تم رصد ملاحظة في حركات البصمة المسجلة لهذا اليوم.";
              let badgeColor = "#d97706";
              let badgeBg = "rgba(245, 158, 11, 0.12)";

              if (kw === 'same_key_repeat') {
                alertTitle = "خطأ بشري: تكرار نفس المفتاح للدخول والخروج";
                alertDesc = `الموظف قام بتسجيل الحضور بمفتاح (${r.in_1_key || 'F1'}) ثم سجل الانصراف بنفس المفتاح (${r.out_1_key || r.in_1_key}) بدلاً من مفتاح الخروج (${r.in_1_key === 'F1' ? 'F2' : 'F4'}). قام النظام الذكي بالتعرف على الحركة وحساب ساعات الدوام الفعلية مع وضع علامة تنبيه للمراجعة.`;
              } else if (kw === 'cross_key') {
                alertTitle = "خطأ بشري: مفاتيح بصمة متقاطعة (Cross-Key)";
                alertDesc = `تم تسجيل الحضور بمفتاح (${r.in_1_key}) والانصراف بمفتاح (${r.out_1_key}). قام النظام بربط الحركتين بنجاح لاحتساب فترة التواجد الفعلية.`;
              } else if (kw === 'reversed_keys') {
                alertTitle = "خطأ بشري: عكس مفاتيح الحضور والانصراف";
                alertDesc = `بدأ الموظف تسجيل الدوام بمفتاح خروج (${r.in_1_key}) ثم سجل بمفتاح دخول (${r.out_1_key}). تم تصحيح التسلسل تلقائياً واحتساب الساعات الفعلية.`;
              } else if (kw === 'started_with_out_key') {
                alertTitle = "بدء التسجيل بمفتاح خروج";
                alertDesc = `بدأ الموظف حركته الأولى بمفتاح انصراف (${r.in_1_key}). تم احتساب الوقت المقضي حتى الانصراف الفعلي.`;
              } else if (kw === 'missing_checkout') {
                alertTitle = "بصمة مفردة: لم يتم تسجيل انصراف";
                alertDesc = "قام الموظف بتسجيل بصمة الحضور فقط ولم يسجل بصمة الانصراف لهذا اليوم. وفقاً للائحة، يُترك الشفت فارغاً ولا يتم احتساب ساعات أو عجز لهذا اليوم.";
                badgeColor = "#ef4444";
                badgeBg = "rgba(239, 68, 68, 0.12)";
              } else if (kw === 'missing_checkin') {
                alertTitle = "بصمة مفردة: لم يتم تسجيل حضور";
                alertDesc = "قام الموظف بتسجيل بصمة الانصراف فقط بدون بصمة حضور سابقة. وفقاً للائحة، يُترك الشفت فارغاً ولا يتم احتساب ساعات أو عجز لهذا اليوم.";
                badgeColor = "#ef4444";
                badgeBg = "rgba(239, 68, 68, 0.12)";
              } else if (kw === 'start_of_24h') {
                alertTitle = "بداية نوبتجية ممتدة (24 ساعة أو أكثر)";
                alertDesc = "تم تسجيل حضور بداية النوبتجية الممتدة. يُعرض وقت الحضور في هذا السطر ويُترك نوع الشفت فارغاً، على أن يُحسب الشفت وساعات العمل في تاريخ الانصراف بالسطر التالي.";
                badgeColor = "#3b82f6";
                badgeBg = "rgba(59, 130, 246, 0.12)";
              } else if (kw === 'end_of_24h') {
                alertTitle = "نهاية نوبتجية ممتدة (انصراف)";
                alertDesc = `تم تسجيل انصراف النوبتجية الممتدة (${r.shift_type}). تم احتساب إجمالي الساعات (${r.time_spent}) والعجز/الإضافي في هذا السطر الخاص بتاريخ الانصراف.`;
                badgeColor = "#10b981";
                badgeBg = "rgba(16, 185, 129, 0.12)";
              } else if (r.is_late_arrival) {
                alertTitle = "تأخير في الحضور عن الموعد المحدد";
                alertDesc = "تم تسجيل الحضور بعد الساعة 08:45 صباحاً (حيث تبدأ فترة الدوام 08:30 ص مع فترة سماح 15 دقيقة حتى 08:45 ص).";
              }

              return (
                <div style={{
                  padding: 14,
                  borderRadius: 'var(--radius-md)',
                  background: badgeBg,
                  border: `1px solid ${badgeColor}40`,
                  marginBottom: 16
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 800, color: badgeColor, fontSize: '0.92rem', marginBottom: 6 }}>
                    <span>⚠️ {alertTitle}</span>
                  </div>
                  <div style={{ fontSize: '0.82rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>
                    {alertDesc}
                  </div>
                </div>
              );
            })()}

            {/* Punches & Biometric Metadata Breakdown */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: 8, color: 'var(--text-muted)' }}>
                تفاصيل حركات البصمة المسجلة:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {/* Check-in Box */}
                <div style={{ padding: 12, borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>حركة الحضور:</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 800, color: selectedAlertRecord.record.check_in_1 ? 'var(--text-primary)' : 'var(--text-muted)', marginBottom: 6 }}>
                    {selectedAlertRecord.record.check_in_1 || '(غير مسجل)'}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: '0.75rem' }}>
                    <div>المفتاح: <strong>{selectedAlertRecord.record.in_1_key || '-'}</strong></div>
                    <div>التحقق: <strong>{selectedAlertRecord.record.in_1_auth_type || '-'}</strong></div>
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={selectedAlertRecord.record.in_1_terminal}>
                      الجهاز: <strong>{selectedAlertRecord.record.in_1_terminal || '-'}</strong>
                    </div>
                  </div>
                </div>

                {/* Check-out Box */}
                <div style={{ padding: 12, borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>حركة الانصراف:</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 800, color: selectedAlertRecord.record.check_out_1 ? 'var(--text-primary)' : 'var(--text-muted)', marginBottom: 6 }}>
                    {selectedAlertRecord.record.check_out_1 || '(غير مسجل)'}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: '0.75rem' }}>
                    <div>المفتاح: <strong>{selectedAlertRecord.record.out_1_key || '-'}</strong></div>
                    <div>التحقق: <strong>{selectedAlertRecord.record.out_1_auth_type || '-'}</strong></div>
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={selectedAlertRecord.record.out_1_terminal}>
                      الجهاز: <strong>{selectedAlertRecord.record.out_1_terminal || '-'}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Calculations & Decision Status */}
            <div style={{ padding: 12, borderRadius: 'var(--radius-md)', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', marginBottom: 18 }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, marginBottom: 8, color: 'var(--text-muted)' }}>
                نتائج الاحتساب المالي والإداري:
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>نوع الشفت</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 800 }}>{selectedAlertRecord.record.shift_type || '(فارغ)'}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>الوقت المقضي</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 800 }}>{selectedAlertRecord.record.time_spent || '0:00'}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>وقت العجز/التأخير</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 800, color: selectedAlertRecord.record.is_deficit ? 'var(--peach-text)' : 'inherit' }}>
                    {selectedAlertRecord.record.deficit_time || '0:00'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>الوقت الإضافي</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 800, color: selectedAlertRecord.record.is_overtime ? 'var(--mint-text)' : 'inherit' }}>
                    {selectedAlertRecord.record.overtime_time || '0:00'}
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              <button
                type="button"
                onClick={() => setSelectedAlertRecord(null)}
                className="btn-primary"
                style={{ padding: '8px 20px', fontSize: '0.85rem' }}
              >
                إغلاق
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 6. TOAST NOTIFICATIONS CONTAINER */}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast toast-${toast.type}`}>
            <div style={{ flexShrink: 0, marginTop: 2 }}>
              {toast.type === 'success' && <CheckCircle2 size={18} color="#10B981" />}
              {toast.type === 'error' && <AlertCircle size={18} color="#EF4444" />}
              {toast.type === 'warning' && <AlertTriangle size={18} color="#F59E0B" />}
              {toast.type === 'info' && <Sparkles size={18} color="#3B82F6" />}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: '0.88rem' }}>{toast.title}</div>
              {toast.message && (
                <div style={{ fontSize: '0.78rem', opacity: 0.9, marginTop: 2 }}>
                  {toast.message}
                </div>
              )}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              style={{ background: 'none', border: 'none', color: 'inherit', opacity: 0.7, cursor: 'pointer', padding: 2 }}
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>

    </div>
  );
}
