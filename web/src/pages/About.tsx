import type { AcademicData } from "../domain";
import { AcademicNotice, Badge } from "../components/Common";

export function AboutPage({ data }: { data: AcademicData }) {
  const statusCounts = data.questions.reduce<Record<string, number>>(
    (counts, question) => {
      counts[question.answer_status] = (counts[question.answer_status] ?? 0) + 1;
      return counts;
    },
    {},
  );
  return (
    <div className="page page--reader">
      <header className="page-header">
        <span className="eyebrow">Evidence, privacy, and limitations</span>
        <h1>About the academic data</h1>
        <p lang="th">
          วิธีจัดเตรียมข้อมูล ความหมายของสถานะคำตอบ และข้อจำกัดที่ผู้เรียนควรรู้
        </p>
      </header>

      <div className="about-grid">
        <article className="reading-card">
          <h2>Local by design</h2>
          <p>
            The application bundles validated JSON generated from the supplied
            local materials. It has no account, backend, analytics, telemetry,
            or academic-file upload. Progress lives in this browser.
          </p>
          <p lang="th">
            แอปใช้ข้อมูล JSON ที่ตรวจสอบแล้ว ไม่มีบัญชีผู้ใช้ Backend Analytics
            หรือการอัปโหลดเอกสาร และเก็บความก้าวหน้าใน Browser นี้เท่านั้น
          </p>
        </article>
        <article className="reading-card">
          <h2>Corpus snapshot</h2>
          <dl className="about-stats">
            <div><dt>Subjects</dt><dd>{data.subjects.length}</dd></div>
            <div><dt>Chapters</dt><dd>{data.chapters.length}</dd></div>
            <div><dt>Topics</dt><dd>{data.topics.length}</dd></div>
            <div><dt>Questions</dt><dd>{data.questions.length}</dd></div>
          </dl>
        </article>
      </div>

      <section>
        <div className="section-heading">
          <div>
            <span className="eyebrow">Answer status</span>
            <h2>What each label means</h2>
          </div>
        </div>
        <div className="definition-grid">
          <article>
            <Badge tone="success">
              Course verified · {statusCounts.verified_from_course_material ?? 0}
            </Badge>
            <h3>Verified from course materials</h3>
            <p>The answer is directly supported by a cited supplied learning source.</p>
          </article>
          <article>
            <Badge tone="success">
              External verified · {statusCounts.verified_from_external_source ?? 0}
            </Badge>
            <h3>Verified from external sources</h3>
            <p>The answer is supported by inspected authoritative external evidence.</p>
          </article>
          <article>
            <Badge tone="warning">
              Strong external · {statusCounts.strongly_supported_by_external_source ?? 0}
            </Badge>
            <h3>Supported, not fully definitive</h3>
            <p>These items are mock-exam opt-in and retain human review.</p>
          </article>
          <article>
            <Badge tone="warning">
              Probability only · {statusCounts.probabilistic_recommendation ?? 0}
            </Badge>
            <h3>Recommendation, not verification</h3>
            <p>These questions are available only in the judgment practice queue and remain unscored.</p>
          </article>
          <article>
            <Badge tone="danger">
              Unresolved · {statusCounts.unresolvable_question ?? 0}
            </Badge>
            <h3>No defensible answer</h3>
            <p>Defective or under-specified questions are excluded from scored examinations.</p>
          </article>
        </div>
      </section>

      <AcademicNotice title="BIS603 mapping warning">
        <p>
          The strategy and marketing content is clear, but no sampled
          authoritative outline verifies the exact supplied BIS603 code-title
          pairing. The subject page retains medium confidence.
        </p>
      </AcademicNotice>

      <section className="reading-card">
        <h2>Important limitations</h2>
        <ul className="spaced-list">
          <li>English original questions and choices remain authoritative beside Thai.</li>
          <li>Long Thai distractors benefit from a final native-speaker review before high-stakes use.</li>
          <li>Some diagram/table-dependent questions cannot display their missing visual context in version 1.</li>
          <li>Seventy-one authoritative learning/exam files support the structured data; all 374 original files remain inventoried locally.</li>
          <li>Question numbers 11–18 are absent from the supplied practice PDF; question 113 is present and included.</li>
        </ul>
      </section>
    </div>
  );
}
