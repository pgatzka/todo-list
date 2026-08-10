/**
 * Provisional shape of a todo, enough to prove the package resolves from both
 * halves of the workspace. The real data model — notes, due date, priority,
 * tags — is decided by ADR-0003 (#27); expect every field here to be revisited
 * there.
 */
export type Todo = {
  readonly id: string;
  readonly title: string;
  readonly completed: boolean;
};
